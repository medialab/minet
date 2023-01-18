# =============================================================================
# Minet YouTube Formatters
# =============================================================================
#
# Various data formatters for YouTube data.
#
from casanova import namedrecord
from ebbe import getpath

from minet.youtube.constants import (
    YOUTUBE_VIDEO_CSV_HEADERS,
    YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS,
    YOUTUBE_PLAYLIST_VIDEO_SNIPPET_CSV_HEADERS,
    YOUTUBE_COMMENT_CSV_HEADERS,
    YOUTUBE_CHANNEL_CSV_HEADERS,
)

YouTubeVideo = namedrecord(
    "YouTubeVideo", YOUTUBE_VIDEO_CSV_HEADERS, boolean=["has_caption"]
)

YouTubeVideoSnippet = namedrecord(
    "YouTubeVideoSnippet", YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS
)

YouTubePlaylistVideoSnippet = namedrecord(
    "YouTubePlaylistVideoSnippet", YOUTUBE_PLAYLIST_VIDEO_SNIPPET_CSV_HEADERS
)

YouTubeComment = namedrecord("YoutubeComment", YOUTUBE_COMMENT_CSV_HEADERS)

YouTubeChannel = namedrecord(
    "YoutubeChannel",
    YOUTUBE_CHANNEL_CSV_HEADERS,
    boolean=["moderate_comments", "made_for_kids"],
    plural=["topic_ids", "topic_categories", "topic_keywords", "keywords"],
)


def get_int(item, key):
    nb = item.get(key)

    if nb is not None:
        return int(nb)

    return nb


def format_video(item):
    snippet = item["snippet"]
    stats = item["statistics"]
    details = item["contentDetails"]

    row = YouTubeVideo(
        item["id"],
        snippet["publishedAt"],
        snippet["channelId"],
        snippet["title"],
        snippet["description"],
        snippet["channelTitle"],
        get_int(stats, "viewCount"),
        get_int(stats, "likeCount"),
        # get_int(stats, 'dislikeCount'),
        # get_int(stats, 'favoriteCount'),
        get_int(stats, "commentCount"),
        details["duration"],
        details["caption"] == "true",
    )

    return row


def format_video_snippet(item):
    snippet = item["snippet"]

    row = YouTubeVideoSnippet(
        item["id"]["videoId"],
        snippet["publishedAt"],
        snippet["channelId"],
        snippet["title"],
        snippet["description"],
        snippet["channelTitle"],
    )

    return row


def format_comment(item):
    meta = item["snippet"]
    snippet = getpath(item, ["snippet", "topLevelComment", "snippet"])

    row = YouTubeComment(
        meta["videoId"],
        item["id"],
        snippet["authorDisplayName"],
        getpath(snippet, ["authorChannelId", "value"]),
        snippet["textOriginal"],
        int(snippet["likeCount"]),
        snippet["publishedAt"],
        snippet["updatedAt"],
        int(meta["totalReplyCount"]),
        None,
    )

    return row


def format_reply(item, video_id=None):
    snippet = item["snippet"]

    row = YouTubeComment(
        video_id if video_id is not None else snippet["videoId"],
        item["id"],
        snippet["authorDisplayName"],
        getpath(snippet, ["authorChannelId", "value"]),
        snippet["textOriginal"],
        int(snippet["likeCount"]),
        snippet["publishedAt"],
        snippet["updatedAt"],
        None,
        snippet["parentId"],
    )

    return row


def format_playlist_item_snippet(item):
    snippet = item["snippet"]

    row = YouTubePlaylistVideoSnippet(
        snippet["resourceId"]["videoId"],
        snippet["publishedAt"],
        snippet["channelId"],
        snippet["title"],
        snippet["description"],
        snippet["channelTitle"],
        snippet["position"],
    )

    return row


def format_channel(item):
    snippet = item.get("snippet")
    statistics = item.get("statistics")
    topic_details = item.get("topicDetails")
    status = item.get("status")
    branding_settings = item.get("brandingSettings")

    topic_keywords = [url.rsplit("/", 1)[1] for url in topic_details["topicCategories"]]

    keywords = getpath(branding_settings, ["channel", "keywords"])
    if keywords:
        keywords = [
            keyword.strip() for keyword in keywords.split('"') if keyword.strip()
        ]

    row = YouTubeChannel(
        item.get("id"),
        snippet.get("title"),
        snippet.get("description"),
        snippet.get("customUrl"),
        snippet.get("publishedAt"),
        getpath(snippet, ["thumbnails", "high", "url"]),
        snippet.get("defaultLanguage"),
        snippet.get("country"),
        getpath(item, ["contentDetails", "relatedPlaylists", "uploads"]),
        statistics.get("viewCount"),
        statistics.get("hiddenSubscriberCount"),
        statistics.get("subscriberCount"),
        statistics.get("videoCount"),
        topic_details.get("topicIds"),
        topic_details.get("topicCategories"),
        topic_keywords,
        status.get("privacyStatus"),
        status.get("madeForKids"),
        status.get("longUploadsStatus"),
        keywords,
        getpath(branding_settings, ["channel", "moderateComments"]),
        getpath(branding_settings, ["channel", "unsubscribedTrailer"]),
        getpath(branding_settings, ["image", "bannerExternalUrl"]),
    )

    return row
