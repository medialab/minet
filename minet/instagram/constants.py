# =============================================================================
# Minet Instagram Constants
# =============================================================================
#
# General constants used throughout the Instagram functions.
#
from urllib3 import Timeout

INSTAGRAM_URL = "https://www.instagram.com"
INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 2)
INSTAGRAM_POST_CSV_HEADERS = [
    "comments_disabled",
    "typename",
    "id",
    "edge_media_to_caption_edges",
    "shortcode",
    "edge_media_to_comment_count",
    "taken_at_timestamp",
    "display_url",
    "edge_liked_by_count",
    "edge_media_preview_like_count",
    "owner_id",
    "is_video",
    "accessibility_caption",
]
