from typing import Optional, List, Tuple

from ural import URLFormatter, urlpathsplit

from minet.bluesky.constants import (
    BLUESKY_HTTP_API_BASE_URL,
    BLUESKY_HTTP_API_ALTERNATE_URL,
)


def parse_post_url(url: str) -> Tuple[str, str]:
    path = urlpathsplit(url)

    did = path[1]
    rkey = path[3]

    return did, rkey


def format_post_at_uri(did: str, rkey: str) -> str:
    return "at://{}/app.bsky.feed.post/{}".format(did, rkey)


class BlueskyHTTPAPIUrlFormatter(URLFormatter):
    BASE_URL = BLUESKY_HTTP_API_BASE_URL

    def create_session(self) -> str:
        return self.format(
            path="com.atproto.server.createSession",
        )

    def refresh_session(self) -> str:
        return self.format(path="com.atproto.server.refreshSession")

    def resolve_handle(self, handle: str) -> str:
        # Handles resolving of special handles based on a different DNS do not work on the regular API, we need to use the alternate endpoint from the public facing API
        # cf https://github.com/bluesky-social/indigo/issues/833
        return self.format(
            base_url=BLUESKY_HTTP_API_ALTERNATE_URL,
            path="com.atproto.identity.resolveHandle",
            args={"handle": handle},
        )

    def get_posts(self, uris: List[str]) -> str:
        return self.format(
            path="app.bsky.feed.getPosts", args=[("uris", uri) for uri in uris]
        )

    def get_profiles(self, identifiers: List[str]) -> str:
        return self.format(
            path="app.bsky.actor.getProfiles",
            args=[("actors", identifier) for identifier in identifiers],
        )

    def search_posts(
        self, q: str, cursor: Optional[str] = None, limit: int = 100
    ) -> str:
        return self.format(
            path="app.bsky.feed.searchPosts",
            args={"q": q, "cursor": cursor, "limit": limit},
        )
