from typing import Optional, Iterable

from ural import URLFormatter

from minet.youtube.constants import (
    YOUTUBE_API_BASE_URL,
    YOUTUBE_API_MAX_VIDEOS_PER_CALL,
)


class YouTubeAPIURLFormatter(URLFormatter):
    BASE_URL = YOUTUBE_API_BASE_URL

    def __init__(self):
        def format_arg_value(k, v):
            if isinstance(v, Iterable):
                return ",".join(v)

            return v

        super().__init__(format_arg_value=format_arg_value)

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
