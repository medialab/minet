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
