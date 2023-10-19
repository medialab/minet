from typing import Optional, List

from casanova import TabularRecord
from dataclasses import dataclass


def get_int(item, key) -> Optional[int]:
    nb = item.get(key)

    if nb is not None:
        return int(nb)

    return None


@dataclass
class YouTubeCaptionTrack(TabularRecord):
    lang: str
    url: str
    generated: bool


@dataclass
class YouTubeCaptionLine(TabularRecord):
    start: float
    duration: float
    text: str


@dataclass
class YouTubeVideoSnippet(TabularRecord):
    video_id: str
    title: str
    published_at: str
    description: str
    channel_id: str
    channel_title: str


@dataclass
class YouTubePlaylistVideoSnippet(YouTubeVideoSnippet):
    position: int


@dataclass
class YouTubeVideo(YouTubeVideoSnippet):
    view_count: Optional[int]
    like_count: Optional[int]
    # dislike_count: int # NOTE: This property is deprecated since december 13th 2021.
    # favorite_count: int # NOTE: This property has been deprecated by YouTube in 2015. The property's value is now always set to 0.
    comment_count: Optional[int]
    duration: str
    has_captions: bool

    @classmethod
    def from_payload(cls, payload) -> "YouTubeVideo":
        snippet = payload["snippet"]
        stats = payload["statistics"]
        details = payload["contentDetails"]

        return YouTubeVideo(
            video_id=payload["id"],
            published_at=snippet["publishedAt"],
            channel_id=snippet["channelId"],
            title=snippet["title"],
            description=snippet["description"],
            channel_title=snippet["channelTitle"],
            view_count=get_int(stats, "viewCount"),
            like_count=get_int(stats, "likeCount"),
            comment_count=get_int(stats, "commentCount"),
            duration=details["duration"],
            has_captions=details["caption"] == "true",
        )


@dataclass
class YouTubeComment(TabularRecord):
    video_id: str
    comment_id: str
    author_name: str
    author_channel_id: str
    text: str
    like_count: int
    published_at: str
    updated_at: str
    reply_count: int
    parent_comment_id: Optional[str]


@dataclass
class YouTubeChannel(TabularRecord):
    channel_id: str
    title: str
    description: str
    custom_url: str
    published_at: str
    thumbnail: str
    default_language: str
    country: str
    id_playlists_videos: List[str]
    view_count: int
    hidden_subscriber_count: int
    subscriber_count: int
    video_count: int
    topic_ids: List[str]
    topic_categories: List[str]
    topic_keywords: List[str]
    privacy_status: str
    made_for_kids: bool
    long_uploads_status: str
    keywords: List[str]
    moderate_comments: bool
    unsubscribed_trailer: str
    banner_external_url: str
