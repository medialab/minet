# =============================================================================
# Minet Tiktok Constants
# =============================================================================
#
# General constants used throughout the Tiktok functions.
#
from urllib3 import Timeout

TIKTOK_URL = "https://www.tiktok.com"
TIKTOK_PUBLIC_API_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 2)
TIKTOK_DEFAULT_THROTTLE = 3.0
TIKTOK_MIN_TIME_RETRYER = 5.0
TIKTOK_MAX_RANDOM_ADDENDUM = 1.0

TIKTOK_VIDEO_CSV_HEADERS = [
    "id",
    "description",
    "timestamp",
    "utc_time",
    "original_item",
    "video_id",
    "video_height",
    "video_width",
    "video_duration",
    "video_ratio",
    "video_cover",
    "video_origin_cover",
    "video_dynamic_cover",
    # Access denied
    # "video_download_addr",
    "video_reflow_cover",
    "video_bitrate",
    "video_format",
    "video_quality",
    "author_id",
    "author_unique_id",
    "author_nickname",
    "author_avatar",
    "author_signature",
    "author_verified",
    "author_secret",
    "author_following_count",
    "author_follower_count",
    "author_heart_count",
    "author_video_count",
    "author_digg_count",
    "music_id",
    "music_title",
    "music_author_name",
    "music_original",
    "music_play_url",
    "music_duration",
    "music_album",
    "digg_count",
    "share_count",
    "comment_count",
    "play_count",
    "duet_from_video_id",
    "duet_from_user_id",
    "duet_from_user_name",
    "duet_from_user_is_commerce",
    "challenges_titles",
    "challenges_descriptions",
    "stickers_texts",
    "effect_stickers_names",
    "duet_enabled",
    "stitch_enabled",
    "share_enabled",
    "is_ad",
]
