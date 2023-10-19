from typing import Optional, List

from casanova import TabularRecord
from dataclasses import dataclass
from ebbe import getpath


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

    @classmethod
    def from_payload(cls, payload) -> "YouTubeVideoSnippet":
        snippet = payload["snippet"]

        return cls(
            video_id=payload["id"]["videoId"],
            published_at=snippet["publishedAt"],
            channel_id=snippet["channelId"],
            channel_title=snippet["title"],
            description=snippet["description"],
            title=snippet["channelTitle"],
        )


@dataclass
class YouTubePlaylistVideoSnippet(YouTubeVideoSnippet):
    position: int

    @classmethod
    def from_payload(cls, payload) -> "YouTubePlaylistVideoSnippet":
        snippet = payload["snippet"]

        return cls(
            video_id=snippet["resourceId"]["videoId"],
            published_at=snippet["publishedAt"],
            channel_id=snippet["channelId"],
            title=snippet["title"],
            description=snippet["description"],
            channel_title=snippet["channelTitle"],
            position=snippet["position"],
        )


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

        return cls(
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
    reply_count: Optional[int]
    parent_comment_id: Optional[str]

    @classmethod
    def from_parent_comment_payload(cls, payload) -> "YouTubeComment":
        meta = payload["snippet"]
        snippet = getpath(payload, ["snippet", "topLevelComment", "snippet"])

        return cls(
            meta["videoId"],
            payload["id"],
            snippet["authorDisplayName"],
            getpath(snippet, ["authorChannelId", "value"]),
            snippet["textOriginal"],
            int(snippet["likeCount"]),
            snippet["publishedAt"],
            snippet["updatedAt"],
            int(meta["totalReplyCount"]),
            None,
        )

    @classmethod
    def from_reply_payload(
        cls, payload, video_id: Optional[str] = None
    ) -> "YouTubeComment":
        snippet = payload["snippet"]

        return cls(
            video_id if video_id is not None else snippet["videoId"],
            payload["id"],
            snippet["authorDisplayName"],
            getpath(snippet, ["authorChannelId", "value"]),
            snippet["textOriginal"],
            int(snippet["likeCount"]),
            snippet["publishedAt"],
            snippet["updatedAt"],
            None,
            snippet["parentId"],
        )


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

    @classmethod
    def from_payload(cls, payload) -> "YouTubeChannel":
        snippet = payload.get("snippet")
        statistics = payload.get("statistics")
        topic_details = payload.get("topicDetails", {})
        status = payload.get("status")
        branding_settings = payload.get("brandingSettings")

        topic_ids = topic_details.get("topicIds", [])
        topic_categories = topic_details.get("topicCategories", [])
        topic_keywords = [url.rsplit("/", 1)[1] for url in topic_categories]

        keywords = getpath(branding_settings, ["channel", "keywords"])
        if keywords:
            keywords = [
                keyword.strip() for keyword in keywords.split('"') if keyword.strip()
            ]

        return YouTubeChannel(
            payload.get("id"),
            snippet.get("title"),
            snippet.get("description"),
            snippet.get("customUrl"),
            snippet.get("publishedAt"),
            getpath(snippet, ["thumbnails", "high", "url"]),
            snippet.get("defaultLanguage"),
            snippet.get("country"),
            getpath(payload, ["contentDetails", "relatedPlaylists", "uploads"]),
            statistics.get("viewCount"),
            statistics.get("hiddenSubscriberCount"),
            statistics.get("subscriberCount"),
            statistics.get("videoCount"),
            topic_ids,
            topic_categories,
            topic_keywords,
            status.get("privacyStatus"),
            status.get("madeForKids"),
            status.get("longUploadsStatus"),
            keywords,
            getpath(branding_settings, ["channel", "moderateComments"]),
            getpath(branding_settings, ["channel", "unsubscribedTrailer"]),
            getpath(branding_settings, ["image", "bannerExternalUrl"]),
        )
