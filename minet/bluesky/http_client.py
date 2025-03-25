from typing import Iterator, Iterable, Optional, Any, List, Dict

from time import time, sleep
from ebbe import as_reconciled_chunks

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
from minet.bluesky.types import BlueskyPost
from minet.bluesky.exceptions import (
    BlueskyAuthenticationError,
    BlueskySessionRefreshError,
)


class BlueskyHTTPClient:
    def __init__(self, identifier: str, password: str):
        self.urls = BlueskyHTTPAPIUrlFormatter()
        self.pool_manager = create_pool_manager()
        self.retryer = create_request_retryer()
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

        remaining = int(response.headers["RateLimit-Remaining"])

        if remaining <= 0:
            self.rate_limit_reset = int(response.headers["RateLimit-Reset"])

        return response

    def search_posts(self, query: str) -> Iterator[BlueskyPost]:
        cursor = None

        while True:
            url = self.urls.search_posts(query, cursor=cursor)

            response = self.request(url)
            data = response.json()

            for post in data["posts"]:
                yield BlueskyPost.from_payload(post)

            cursor = data.get("cursor")

            if cursor is None:
                break

    def resolve_handle(self, identifier: str) -> str:
        url = self.urls.resolve_handle(identifier)

        response = self.request(url)
        data = response.json()

        return data["did"]

    def post_url_to_did_at_uri(self, url: str) -> str:
        handle, rkey = parse_post_url(url)
        did = self.resolve_handle(handle)

        return format_post_at_uri(did, rkey)

    # NOTE: this API route that not return any results for at-uris containing handles!
    def get_posts(self, did_at_uris: Iterable[str]) -> Iterator[Any]:
        def work(chunk: List[str]) -> Dict[str, Any]:
            url = self.urls.get_posts(chunk)
            response = self.request(url)
            data = response.json()

            return {post["uri"]: post for post in data["posts"]}

        def reconcile(data: Dict[str, Any], uri: str) -> Any:
            return data.get(uri)

        for _, post_data in as_reconciled_chunks(25, did_at_uris, work, reconcile):
            yield post_data

    def get_profiles(self, identifiers: Iterable[str]) -> Iterator[Any]:
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
            yield profile_data
