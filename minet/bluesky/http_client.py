from typing import Iterator

from minet.web import (
    create_request_retryer,
    create_pool_manager,
    retrying_method,
    request,
    Response,
)

from minet.bluesky.urls import BlueskyHTTPAPIUrlFormatter
from minet.bluesky.jwt import parse_jwt_for_expiration
from minet.bluesky.types import BlueskyPost


# TODO: token refresh, split request method in specifics for create_session and refresh_session


class BlueskyHTTPClient:
    def __init__(self, identifier: str, password: str):
        self.urls = BlueskyHTTPAPIUrlFormatter()
        self.pool_manager = create_pool_manager()
        self.retryer = create_request_retryer()

        response = self.request(
            self.urls.create_session(),
            method="POST",
            json_body={"identifier": identifier, "password": password},
            unauthenticated=True,
        ).json()

        self.access_jwt = response["accessJwt"]
        self.refresh_jwt = response["refreshJwt"]

        self.access_jwt_expiration = parse_jwt_for_expiration(self.access_jwt)

    @retrying_method()
    def request(
        self,
        url: str,
        method: str = "GET",
        json_body=None,
        unauthenticated: bool = False,
    ) -> Response:
        headers = {}

        if not unauthenticated:
            headers["Authorization"] = "Bearer {}".format(self.access_jwt)

        response = request(
            url,
            pool_manager=self.pool_manager,
            method=method,
            json_body=json_body,
            known_encoding="utf-8",
            headers=headers,
        )

        return response

    def search_posts(self, query: str) -> Iterator[BlueskyPost]:
        url = self.urls.search_posts(query)

        response = self.request(url)

        for post in response.json()["posts"]:
            yield BlueskyPost.from_payload(post)
