# =============================================================================
# Minet Instagram Constants
# =============================================================================
#
# General constants used throughout the Instagram functions.
#
from pickle import INST
from urllib3 import Timeout

INSTAGRAM_URL = "https://www.instagram.com"
INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 2)
INSTAGRAM_DEFAULT_THROTTLE = 30.0
INSTAGRAM_MEDIA_TYPE = {1: "GraphImage", 2: "GraphVideo", 8: "GraphSidecar"}
INSTAGRAM_MAX_RANDOM_ADDENDUM = 10.0
INSTAGRAM_DEFAULT_THROTTLE_EVERY_10_CALLS = 300.0
INSTAGRAM_MAX_RANDOM_ADDENDUM_EVERY_10_CALLS = 300.0
INSTAGRAM_DEFAULT_THROTTLE_EVERY_2900_CALLS = 1800.0
INSTAGRAM_MAX_RANDOM_ADDENDUM_EVERY_2900_CALLS = 1800.0
INSTAGRAM_MIN_TIME_RETRYER = 600.0

INSTAGRAM_HASHTAG_POST_CSV_HEADERS = [
    "id",
    "media_type",
    "shortcode",
    "url",
    "caption",
    "hashtags",
    "mentioned_names",
    "liked_by_count",
    "comments_disabled",
    "comment_count",
    "preview_like_count",
    "video_view_count",
    "owner_id",
    "taken_at_timestamp",
    "utc_time",
    "accessibility_caption",
    "display_url",
]

INSTAGRAM_USER_POST_CSV_HEADERS = [
    "id",
    "media_type",
    "shortcode",
    "url",
    "caption",
    "hashtags",
    "mentioned_names",
    "like_and_view_counts_disabled",
    "like_count",
    "comment_count",
    "video_view_count",
    "video_title",
    "video_duration",
    "taken_at_timestamp",
    "utc_time",
]

INSTAGRAM_USER_FOLLOW_CSV_HEADERS = [
    "pk",
    "username",
    "full_name",
    "is_private",
    "profile_pic_url",
    "profile_pic_id",
    "is_verified",
    "has_anonymous_profile_picture",
    "has_highlight_reels",
    "account_badges",
    "similar_user_id",
    "latest_reel_media",
    "is_favorite",
]
