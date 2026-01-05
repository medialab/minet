from typing import Iterator, Iterable, Optional, Any, List, Dict, Union, Tuple

from time import time, sleep
from datetime import datetime, timezone
from ebbe import as_reconciled_chunks

from twitwi.utils import get_dates
from twitwi.bluesky import normalize_profile, normalize_post, normalize_partial_profile
from twitwi.bluesky.types import BlueskyPost, BlueskyProfile, BlueskyPartialProfile
from twitwi.constants import SOURCE_DATETIME_FORMAT_V2

from minet.web import (
    create_request_retryer,
    create_pool_manager,
    retrying_method,
    request,
    Response,
)

from minet.cli.console import console

from minet.bluesky.urls import (
    BlueskyHTTPAPIUrlFormatter,
    parse_post_url,
    format_post_at_uri,
)
from minet.bluesky.jwt import parse_jwt_for_expiration
from minet.bluesky.exceptions import (
    BlueskyAuthenticationError,
    BlueskyExpiredToken,
    BlueskySessionRefreshError,
    BlueskyBadRequestError,
    BlueskyUpstreamFailureError,
    BlueskyHandleNotFound,
)


class BlueskyHTTPClient:
    def __init__(self, identifier: str, password: str):
        self.urls = BlueskyHTTPAPIUrlFormatter()
        self.pool_manager = create_pool_manager()
        self.retryer = create_request_retryer(
            additional_exceptions=[BlueskyUpstreamFailureError, BlueskyExpiredToken], retry_on_statuses=[502]
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
            raise_on_statuses=[502],
        )

        if response.status >= 400:
            data = response.json()
            if "error" in data:
                e = data["error"]
                if e == "UpstreamFailure":
                    raise BlueskyUpstreamFailureError(
                        f"Bluesky is currently experiencing upstream issues. (HTTP status {response.status})"
                    )
                # Somehow happens after 2 hours on a request (which worked fine before)
                # It doesn't happen very often
                if e == "ExpiredToken":
                    raise BlueskyExpiredToken(
                        f"{data['message']}. On url: {url} (HTTP {response.status})"
                    )
                raise BlueskyBadRequestError(
                    f"HTTP {response.status} {e}: {data['message']}"
                )
            raise BlueskyBadRequestError(f"HTTP {response.status}")

        remaining = int(response.headers["RateLimit-Remaining"])

        if remaining <= 0:
            self.rate_limit_reset = int(response.headers["RateLimit-Reset"])

        return response

    def post_quotes(self, post_uri: str) -> Iterator[BlueskyPost]:
        cursor = None

        while True:
            url = self.urls.post_quotes(post_uri, cursor=cursor)

            response = self.request(url)
            data = response.json()

            for post in data["posts"]:
                yield normalize_post(post)

            cursor = data.get("cursor")

            if cursor is None:
                break

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
        store_errors: bool = False,
    ) -> Iterator[Union[BlueskyPost, Tuple[str, str]]]:
        cursor = None
        oldest_post_uris: set[str] = set()
        new_oldest_post_uris: set[str] = set()
        oldest_post_timestamp_utc = None  # has millisecond precision

        # Search with time seems to work with millisecond precision
        time_overlap = 1

        # to avoid infinite loop when we find the final post,
        # as it will always appears in the next request because of the time overlap for paging with time range
        oldest_date_changed: bool = False
        oldest_uris_len_changed: bool = False
        old_len_oldest_post_uris = 0

        old_cursor = None

        while True:
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
                console.print(
                    f"There is no post anymore in 'data'. Retrying one time just in case...\n====DATA====\n{data}\n============",
                    highlight=True,
                    style="dim",
                )
                response = self.request(request_url)
                data = response.json()
                if "posts" not in data or len(data["posts"]) == 0:
                    console.print(
                        "There is still no post in 'data'. Stopping.", style="dim"
                    )
                    break

            oldest_date_changed = False
            oldest_uris_len_changed = False
            old_len_oldest_post_uris = len(oldest_post_uris)
            new_oldest_post_uris.clear()

            for post in data["posts"]:
                # We're using the uri as a unique identifier for posts, as there exists cids that are not
                if post["uri"] in oldest_post_uris:
                    continue

                try:
                    # TODO : handle locale + extract_referenced_posts + collected_via
                    yield normalize_post(post)
                except Exception as e:
                    if store_errors:
                        yield (str(e), post)
                    else:
                        raise e

                # Taking the minimum createdAt time to avoid issues
                # with posts not being perfectly sorted by createdAt (local_time parameter is createdAt in UTC)
                # TODO: handle locale timezone wanted by user
                post_timestamp_utc = get_dates(
                    post["record"]["createdAt"],
                    source="bluesky",
                    millisecond_timestamp=True,
                )[0]

                if (
                    oldest_post_timestamp_utc
                    and oldest_post_timestamp_utc <= post_timestamp_utc
                ):
                    if post_timestamp_utc == oldest_post_timestamp_utc:
                        # adding posts within the time range of the oldest post to the "already seen uris" list,
                        # because they will be in the next request because of the little
                        # (but still existing) time overlap for paging with time range
                        if not oldest_date_changed:
                            oldest_post_uris.add(post["uri"])
                        else:
                            # Not changing oldest_post_uris yet, as we still need to check all posts in this request,
                            # in case we (unfortunately and unlikely) encounter an already seen post (in the previous request to the API)
                            # that is older than the current post date (as said, it's unlikely to happen, but we must handle it anyway)
                            new_oldest_post_uris.add(post["uri"])
                    continue

                # We have a new oldest post date
                oldest_date_changed = True
                oldest_uris_len_changed = True
                new_oldest_post_uris.clear()
                new_oldest_post_uris.add(post["uri"])
                oldest_post_timestamp_utc = post_timestamp_utc

            if oldest_date_changed:
                oldest_post_uris.clear()
                oldest_post_uris = new_oldest_post_uris.copy()
                new_oldest_post_uris.clear()

            # We are not changing the oldest_post_uris manually in the loop,
            # as oldest_post_uris is only changed by adding NEW uris,
            # and uris already in the set are ignored when added again, i.e. the set isn't changed,
            # except in the case where the oldest post date changes.
            if not oldest_date_changed:
                oldest_uris_len_changed = (
                    len(oldest_post_uris) > old_len_oldest_post_uris
                )

            cursor = data.get("cursor")

            # If the oldest post date did not change, no new uris were added to the "already seen uris" list,
            # and the cursor didn't advance further it means we have reached the end of the available posts.
            # NOTE: due to the 10,000 posts limit per search query and the method we use to page with time ranges,
            #       if there is more than 10,000 unique posts with the same date, we won't be able to get them all.
            #       Moreover, when reaching that limit and time paging, we noticed that Bluesky API doesn't return
            #       exactly the same 10,000 posts again: some new posts are found, but most are already seen, and
            #       most importantly it seems that there is no logic behind the order of these posts, meaning
            #       we are for now unable to retrieve the exact same posts when executing the same command
            #       multiple time...
            #       To be investigated...
            if (
                not oldest_uris_len_changed
                and not oldest_date_changed
                and cursor == old_cursor
                and len(oldest_post_uris) <= 10000
            ):
                console.print(
                    f"The oldest post date did not change, no new uris were added to the 'already seen uris' list and we reached the same point as before (cursor = [blue]{cursor}[/blue]).",
                    style="yellow",
                )
                break

            if len(oldest_post_uris) > 10000:
                console.print(
                    f"There is more than 10,000 posts with the same date ([blue]{datetime.fromtimestamp(oldest_post_timestamp_utc / 1000, tz=timezone.utc).strftime(SOURCE_DATETIME_FORMAT_V2) if oldest_post_timestamp_utc else 'N/A'}[/blue]), we will continue paging with time ranges to try to get more posts.",
                    style="yellow",
                )
                oldest_post_timestamp_utc -= time_overlap
                cursor = None  # to force time paging

            if cursor is None:
                # NOTE: the until flag is exclusive
                oldest_post_timestamp_utc_plus_delta = (
                    oldest_post_timestamp_utc + time_overlap
                )

                try:
                    # NOTE: after some testing, it seems that Bluesky limits the number of results to 10,000 posts for search queries.
                    #       That's why we now page with time ranges when we reach that limit, to reset it.
                    until = datetime.fromtimestamp(
                        oldest_post_timestamp_utc_plus_delta / 1000, tz=timezone.utc
                    ).strftime(SOURCE_DATETIME_FORMAT_V2)
                    while "-" in until[:4]:
                        until = "0" + until
                except ValueError as e:
                    # Get your shit together Bluesky...
                    if "out of range" in str(e).lower():
                        break

            # If we added new uris (either with the same oldest post date or a new one, then we're seeing new posts)
            # The only cases we don't update the old_cursor is when we are seeing the same posts again,
            # at the beginning of a new time range page
            if oldest_uris_len_changed:
                old_cursor = cursor

        console.print(f"\t[bold red]Stopping query [blue]{query}[/blue].[/bold red]")

    def search_profiles(self, query: str) -> Iterator[BlueskyPartialProfile]:
        cursor = None
        while True:
            url = self.urls.search_profiles(query, cursor=cursor)

            response = self.request(url)
            data = response.json()

            for profile in data["actors"]:
                yield normalize_partial_profile(profile)

            cursor = data.get("cursor")

            if cursor is None:
                break

    def post_liked_by(self, post_uri: str) -> Iterator[BlueskyPartialProfile]:
        cursor = None

        while True:
            url = self.urls.post_liked_by(post_uri, cursor=cursor)

            response = self.request(url)
            data = response.json()

            for profile in data["likes"]:
                yield normalize_partial_profile(profile["actor"])

            cursor = data.get("cursor")

            if cursor is None:
                break

    def post_reposted_by(self, post_uri: str) -> Iterator[BlueskyPartialProfile]:
        cursor = None

        while True:
            url = self.urls.post_reposted_by(post_uri, cursor=cursor)

            response = self.request(url)
            data = response.json()

            for profile in data["repostedBy"]:
                yield normalize_partial_profile(profile)

            cursor = data.get("cursor")

            if cursor is None:
                break

    def resolve_handle(self, identifier: str, _alternate_api=False) -> str:
        identifier = identifier.lstrip("@")

        url = self.urls.resolve_handle(identifier, _alternate_api=_alternate_api)

        response = self.request(url)
        data = response.json()

        try:
            return data["did"]
        except KeyError:
            if not _alternate_api:
                return self.resolve_handle(identifier, _alternate_api=True)
            else:
                raise BlueskyHandleNotFound(identifier)

    def resolve_post_url(self, url: str) -> str:
        handle, rkey = parse_post_url(url)
        if handle.startswith("did:"):
            did = handle
        else:
            did = self.resolve_handle(handle)

        return format_post_at_uri(did, rkey)

    def profile_follows(self, did: str) -> Iterator[BlueskyPartialProfile]:
        cursor = None

        while True:
            url = self.urls.profile_follows(did, cursor=cursor)
            response = self.request(url)
            data = response.json()

            for profile in data["follows"]:
                yield normalize_partial_profile(profile)

            cursor = data.get("cursor")

            if cursor is None:
                break

    def profile_followers(self, did: str) -> Iterator[BlueskyPartialProfile]:
        cursor = None

        while True:
            url = self.urls.profile_followers(did, cursor=cursor)
            response = self.request(url)
            data = response.json()

            for profile in data["followers"]:
                yield normalize_partial_profile(profile)

            cursor = data.get("cursor")

            if cursor is None:
                break

    # NOTE: this API route does not return any results for at-uris containing handles!
    def posts(
        self, did_at_uris: Iterable[str], return_raw=False
    ) -> Iterator[Optional[Union[BlueskyPost, Dict]]]:
        def work(chunk: List[str]) -> Dict[str, Any]:
            url = self.urls.posts(chunk)
            response = self.request(url)
            data = response.json()

            return {post["uri"]: post for post in data["posts"]}

        def reconcile(data: Dict[str, Any], uri: str) -> Any:
            return data.get(uri)

        for _, post_data in as_reconciled_chunks(25, did_at_uris, work, reconcile):
            if not post_data:
                # in case the post was not found (e.g. non-existing post)
                yield None
            elif return_raw:
                yield post_data
            else:
                # TODO : handle locale + extract_referenced_posts + collected_via
                yield normalize_post(post_data)

    def profile_posts(self, did: str) -> Iterator[BlueskyPost]:
        cursor = None

        while True:
            url = self.urls.profile_posts(did, cursor=cursor)
            response = self.request(url)
            data = response.json()

            for post in data["feed"]:
                # TODO : handle locale + extract_referenced_posts + collected_via
                yield normalize_post(post)

            cursor = data.get("cursor")

            if cursor is None:
                break

    # NOTE: does this need to accept Optional[str]?
    def profiles(
        self, identifiers: Iterable[Optional[str]], return_raw=False
    ) -> Iterator[Optional[Union[BlueskyProfile, Dict]]]:
        def work(chunk: List[str]) -> Dict[str, Any]:
            url = self.urls.profiles(chunk)
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
            if not profile_data:
                # In case the profile was not found (e.g. non-existing user)
                yield None
            elif return_raw:
                yield profile_data
            else:
                # TODO: handle locale + collected_via
                yield normalize_profile(profile_data)
