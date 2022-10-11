# =============================================================================
# Minet Instagram Constants
# =============================================================================
#
# General constants used throughout the Instagram functions.
#
from urllib3 import Timeout

INSTAGRAM_URL = "https://www.instagram.com"
INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 2)
INSTAGRAM_DEFAULT_THROTTLE = 9.0
INSTAGRAM_MEDIA_TYPE = {1: "GraphImage", 2: "GraphVideo", 8: "GraphSidecar"}
INSTAGRAM_HASHTAG_POST_CSV_HEADERS = [
    "id",
    "media_type",
    "shortcode",
    "caption",
    "hashtags",
    "mentioned_names",
    "liked_by_count",
    "comment_count",
    "preview_like_count",
    "video_view_count",
    "owner_id",
    "taken_at_timestamp",
    "accessibility_caption",
    "display_url",
    "comments_disabled",
]

INSTAGRAM_USER_POST_CSV_HEADERS = [
    "id",
    "media_type",
    "shortcode",
    "url",
    "caption",
    # "hashtags",
    # "mentioned_names",
    "like_and_view_counts_disabled",
    "like_count",
    "comment_count",
    "video_view_count",
    "video_title",
    "video_duration",
    "taken_at_timestamp",
    "utc_time"
]
