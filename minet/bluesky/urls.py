from typing import Optional

from ural import URLFormatter

from minet.bluesky.constants import BLUESKY_HTTP_API_BASE_URL


class BlueskyHTTPAPIUrlFormatter(URLFormatter):
    BASE_URL = BLUESKY_HTTP_API_BASE_URL

    def create_session(self) -> str:
        return self.format(
            path="com.atproto.server.createSession",
        )

    def refresh_session(self) -> str:
        return self.format(path="com.atproto.server.refreshSession")

    def search_posts(
        self, q: str, cursor: Optional[str] = None, limit: int = 100
    ) -> str:
        return self.format(
            path="app.bsky.feed.searchPosts",
            args={"q": q, "cursor": cursor, "limit": limit},
        )
