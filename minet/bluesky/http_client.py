from datetime import datetime, timedelta
from typing import Iterator, Iterable, Optional, Any, List, Dict

from time import time, sleep
from ebbe import as_reconciled_chunks

from twitwi.bluesky import normalize_profile, normalize_post
from twitwi.bluesky.types import BlueskyPost, BlueskyProfile
from twitwi.constants import FORMATTED_FULL_DATETIME_FORMAT, SOURCE_DATETIME_FORMAT_V2

from minet.web import (
    create_request_retryer,
    create_pool_manager,
    retrying_method,
    request,
    Response,
)

from minet.bluesky.urls import (
    BlueskyHTTPAPIUrlFormatter,
    parse_post_url,
    format_post_at_uri,
)
from minet.bluesky.jwt import parse_jwt_for_expiration
from minet.bluesky.exceptions import (
    BlueskyAuthenticationError,
    BlueskySessionRefreshError,
    BlueskyBadRequestError,
    BlueskyUpstreamFailureError,
)


class BlueskyHTTPClient:
    def __init__(self, identifier: str, password: str):
        self.urls = BlueskyHTTPAPIUrlFormatter()
        self.pool_manager = create_pool_manager()
        self.retryer = create_request_retryer(
            additional_exceptions=[BlueskyUpstreamFailureError]
        )
        self.rate_limit_reset: Optional[int] = None

        # First auth
        self.create_session(identifier, password)

    @retrying_method()
    def create_session(self, identifier: str, password: str):
        response = request(
            self.urls.create_session(),
            pool_manager=self.pool_manager,
            method="POST",
            json_body={"identifier": identifier, "password": password},
        )

        if response.status != 200:
            raise BlueskyAuthenticationError

        data = response.json()

        self.access_jwt = data["accessJwt"]
        self.refresh_jwt = data["refreshJwt"]
        self.access_jwt_expiration = parse_jwt_for_expiration(self.access_jwt)

    def is_access_jwt_expired(self) -> bool:
        # If the token has 10 seconds left, we consider it expired to avoid network-related issues
        return self.access_jwt_expiration - time() < 10

    @retrying_method()
    def refresh_session(self):
        response = request(
            self.urls.refresh_session(),
            pool_manager=self.pool_manager,
            method="POST",
            headers={"Authorization": "Bearer {}".format(self.refresh_jwt)},
        )

        if response.status != 200:
            raise BlueskySessionRefreshError

        data = response.json()

        self.access_jwt = data["accessJwt"]
        self.refresh_jwt = data["refreshJwt"]
        self.access_jwt_expiration = parse_jwt_for_expiration(self.access_jwt)

    @retrying_method()
    def request(
        self,
        url: str,
        method: str = "GET",
        json_body=None,
    ) -> Response:
        if self.rate_limit_reset is not None:
            sleep(self.rate_limit_reset - time() + 0.1)
            self.rate_limit_reset = None

        if self.is_access_jwt_expired():
            self.refresh_session()

        headers = {"Authorization": "Bearer {}".format(self.access_jwt)}

        response = request(
            url,
            pool_manager=self.pool_manager,
            method=method,
            json_body=json_body,
            known_encoding="utf-8",
            headers=headers,
        )

        if response.status >= 400:
            data = response.json()
            if "error" in data:
                e = data["error"]
                if e == "UpstreamFailure":
                    raise BlueskyUpstreamFailureError(
                        "Bluesky is currently experiencing upstream issues."
                    )
                raise BlueskyBadRequestError(
                    f"HTTP {response.status} {e}: {data['message']}"
                )
            raise BlueskyBadRequestError(f"HTTP {response.status}")

        remaining = int(response.headers["RateLimit-Remaining"])

        if remaining <= 0:
            self.rate_limit_reset = int(response.headers["RateLimit-Reset"])

        return response

    def search_posts(
        self,
        query: str,
        lang: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        mentions: Optional[str] = None,
        author: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Iterator[BlueskyPost]:
        cursor = None
        oldest_post = None
        oldest_post_uris: set[str] = set()
        oldest_post_time_published = None
        normalized_posts: List[BlueskyPost] = []

        # Search with time seems to work with millisecond precision
        time_overlap_delta = timedelta(milliseconds=1)

        # to avoid infinite loop when we find the final post,
        # as it will always appears in the next request because of the time overlap for paging with time range
        found_the_last_post: bool = False
        oldest_date_changed: bool = False
        oldest_uris_changed: bool = False
        old_len_oldest_post_uris = 0

        while not found_the_last_post:

            request_url = self.urls.search_posts(
                q=query,
                cursor=cursor,
                lang=lang,
                since=since,
                until=until,
                mentions=mentions,
                author=author,
                domain=domain,
                url=url,
            )

            response = self.request(request_url)
            data = response.json()

            if "posts" not in data or len(data["posts"]) == 0:
                break

            normalized_posts.clear()

            for post in data["posts"]:
                normalized_post = normalize_post(post)
                normalized_posts.append(normalized_post)
                # We're using the uri as a unique identifier for posts, as it exists cids that are not unique
                if post["uri"] in oldest_post_uris:
                    continue

                # TODO : handle locale + extract_referenced_posts + collected_via
                yield normalized_post

            oldest_post = normalized_posts[-1]

            new_oldest_post_time_published = oldest_post["local_time"]

            oldest_date_changed = False

            # posts are sorted by createdAt to the millisecond precision, so we cut the last 3 digits (that are microseconds)
            if (
                oldest_post_time_published
                and new_oldest_post_time_published[:-3]
                < oldest_post_time_published[:-3]
            ):
                oldest_date_changed = True
                oldest_post_uris.clear()

            oldest_post_time_published = new_oldest_post_time_published

            # adding posts within the time range of the oldest post to the "already seen uris" list,
            # because they will be in the next request because of the little
            # (but still existing) time overlap for paging with time range
            oldest_post_time_published_dt = datetime.strptime(
                oldest_post_time_published, FORMATTED_FULL_DATETIME_FORMAT
            )
            oldest_post_time_published_plus_delta_dt = (
                oldest_post_time_published_dt + time_overlap_delta
            )

            oldest_post_time_published_plus_delta_str = datetime.strftime(
                oldest_post_time_published_plus_delta_dt, FORMATTED_FULL_DATETIME_FORMAT
            )

            old_len_oldest_post_uris = len(oldest_post_uris)

            for post in reversed(normalized_posts):
                post_time_published = post["local_time"]

                # posts are sorted by createdAt to the millisecond precision, so we cut the last 3 digits (that are microseconds)
                if (
                    post_time_published[:-3]
                    > oldest_post_time_published_plus_delta_str[:-3]
                ):
                    break
                oldest_post_uris.add(post["uri"])

            # We are not changing the oldest_post_uris manually in the loop,
            # as oldest_post_uris is only changed by adding NEW uris,
            # and uris already in the set are ignored when added again, i.e. the set isn't changed.
            oldest_uris_changed = len(oldest_post_uris) != old_len_oldest_post_uris

            cursor = data.get("cursor")

            if cursor is None:
                until = oldest_post_time_published_plus_delta_dt.strftime(
                    SOURCE_DATETIME_FORMAT_V2
                )

            # If the oldest post date did not change, and no new uris were added to the "already seen uris" list,
            # it means we have reached the end of the available posts
            found_the_last_post = not oldest_uris_changed and not oldest_date_changed

    def resolve_handle(self, identifier: str, _alternate_api=False) -> str:
        url = self.urls.resolve_handle(identifier, _alternate_api=_alternate_api)

        response = self.request(url)
        data = response.json()
        try:
            return data["did"]
        except KeyError as e:
            if not _alternate_api:
                return self.resolve_handle(identifier, _alternate_api=True)
            else:
                raise e

    def post_url_to_did_at_uri(self, url: str) -> str:
        handle, rkey = parse_post_url(url)
        did = self.resolve_handle(handle)

        return format_post_at_uri(did, rkey)

    # NOTE: this API route does not return any results for at-uris containing handles!
    def get_posts(
        self, did_at_uris: Iterable[str], return_raw=False
    ) -> Iterator[BlueskyPost]:
        def work(chunk: List[str]) -> Dict[str, Any]:
            url = self.urls.get_posts(chunk)
            response = self.request(url)
            data = response.json()

            return {post["uri"]: post for post in data["posts"]}

        def reconcile(data: Dict[str, Any], uri: str) -> Any:
            return data.get(uri)

        for _, post_data in as_reconciled_chunks(25, did_at_uris, work, reconcile):
            if return_raw:
                yield post_data
            # TODO : handle locale + extract_referenced_posts + collected_via
            else:
                yield normalize_post(post_data)

    def get_user_posts(
        self, identifier: str, limit: Optional[int] = -1
    ) -> Iterator[BlueskyPost]:
        if not identifier.startswith("did:"):
            did = self.resolve_handle(identifier)
        else:
            did = identifier

        cursor = None

        count = 0
        while True:
            url = self.urls.get_user_posts(did, cursor=cursor)

            response = self.request(url)
            data = response.json()

            for post in data["feed"]:
                # TODO : handle locale + extract_referenced_posts + collected_via
                yield normalize_post(post)
                count += 1
                if count == limit:
                    break

            cursor = data.get("cursor")

            if cursor is None or count == limit:
                break

    def get_profiles(self, identifiers: Iterable[str]) -> Iterator[BlueskyProfile]:
        def work(chunk: List[str]) -> Dict[str, Any]:
            url = self.urls.get_profiles(chunk)
            response = self.request(url)
            data = response.json()

            index = {}

            for profile in data["profiles"]:
                index[profile["did"]] = profile
                index[profile["handle"]] = profile

            return index

        def reconcile(data: Dict[str, Any], identifier: str) -> Any:
            return data.get(identifier)

        for _, profile_data in as_reconciled_chunks(25, identifiers, work, reconcile):
            # TODO: handle locale + collected_via
            yield normalize_profile(profile_data)
