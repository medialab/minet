# =============================================================================
# Minet YouTube Constants
# =============================================================================
#
# General constants used throughout the YouTube functions.
#

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
YOUTUBE_API_MAX_VIDEOS_PER_CALL = 50
YOUTUBE_API_MAX_CHANNELS_PER_CALL = 50
YOUTUBE_API_MAX_COMMENTS_PER_CALL = 100

YOUTUBE_API_SEARCH_ORDERS = {
    "relevance",
    "date",
    "rating",
    "viewCount",
    "title",
    "videoCount",
}

YOUTUBE_API_DEFAULT_SEARCH_ORDER = "relevance"

YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS = [
    "video_id",
    "published_at",
    "channel_id",
    "title",
    "description",
    "channel_title",
]

YOUTUBE_PLAYLIST_VIDEO_SNIPPET_CSV_HEADERS = YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS + [
    "position"
]

YOUTUBE_VIDEO_CSV_HEADERS = YOUTUBE_VIDEO_SNIPPET_CSV_HEADERS + [
    "view_count",
    "like_count",
    # 'dislike_count',
    # This property is deprecated since december 13th 2021.
    # 'favorite_count',
    # This property has been deprecated by YouTube in 2015. The property's value is now always set to 0.
    "comment_count",
    "duration",
    "has_caption",
]

YOUTUBE_COMMENT_CSV_HEADERS = [
    "video_id",
    "comment_id",
    "author_name",
    "author_channel_id",
    "text",
    "like_count",
    "published_at",
    "updated_at",
    "reply_count",
    "parent_comment_id",
]

YOUTUBE_CAPTIONS_CSV_HEADERS = ["lang", "generated", "start", "duration", "text"]

YOUTUBE_CHANNEL_CSV_HEADERS = [
    "id",
    "title",
    "description",
    "custom_url",
    "published_at",
    "thumbnail",
    "default_language",
    "country",
    "id_playlists_videos",
    "view_count",
    "hidden_subscriber_count",
    "subscriber_count",
    "video_count",
    "topic_ids",
    "topic_categories",
    "topic_keywords",
    "privacy_status",
    "made_for_kids",
    "long_uploads_status",
    "keywords",
    "moderate_comments",
    "unsubscribed_trailer",
    "banner_external_url",
]
