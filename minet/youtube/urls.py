from typing import Optional, Iterable

from ural import URLFormatter

from minet.youtube.constants import (
    YOUTUBE_API_BASE_URL,
    YOUTUBE_API_MAX_VIDEOS_PER_CALL,
    YOUTUBE_API_MAX_COMMENTS_PER_CALL,
    YOUTUBE_API_DEFAULT_SEARCH_ORDER,
)


class YouTubeAPIURLFormatter(URLFormatter):
    BASE_URL = YOUTUBE_API_BASE_URL

    def format_arg_value(self, _, v):
        if isinstance(v, list):
            return ",".join(v)

        return v

    def playlist_videos(self, playlist_id: str, token: Optional[str]) -> str:
        return self.format(
            path="playlistItems",
            args={
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": YOUTUBE_API_MAX_VIDEOS_PER_CALL,
                "pageToken": token,
            },
        )

    def videos(self, ids: Iterable[str]) -> str:
        return self.format(
            path="videos",
            args={"id": ids, "part": ["snippet", "statistics", "contentDetails"]},
        )

    def channels(self, ids: Iterable[str]) -> str:
        return self.format(
            path="channels",
            args={
                "id": ids,
                "part": [
                    "snippet",
                    "statistics",
                    "contentDetails",
                    "topicDetails",
                    "brandingSettings",
                    "status",
                ],
            },
        )

    def search(
        self,
        query: str,
        order: str = YOUTUBE_API_DEFAULT_SEARCH_ORDER,
        token: Optional[str] = None,
    ) -> str:
        return self.format(
            path="search",
            args={
                "part": "snippet",
                "maxResults": YOUTUBE_API_MAX_VIDEOS_PER_CALL,
                "q": query,
                "type": "video",
                "order": order,
                "pageToken": token,
            },
        )

    def comments(self, video_id: str, token: Optional[str] = None) -> str:
        return self.format(
            path="commentThreads",
            args={
                "videoId": video_id,
                "part": ["snippet", "replies"],
                "maxResults": YOUTUBE_API_MAX_COMMENTS_PER_CALL,
                "pageToken": token,
            },
        )

    def replies(self, comment_id: str, token: Optional[str] = None) -> str:
        return self.format(
            path="comments",
            args={
                "parentId": comment_id,
                "part": "snippet",
                "maxResults": YOUTUBE_API_MAX_COMMENTS_PER_CALL,
                "pageToken": token,
            },
        )
