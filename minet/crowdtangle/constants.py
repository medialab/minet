# =============================================================================
# Minet CrowdTangle Constants
# =============================================================================
#
# General constants used throughout the CrowdTangle functions.
#
from urllib3 import Timeout

CROWDTANGLE_DEFAULT_RATE_LIMIT = 6  # Number of hits per minute
CROWDTANGLE_LINKS_DEFAULT_RATE_LIMIT = 2
CROWDTANGLE_DEFAULT_START_DATE = "2010"

CROWDTANGLE_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 5)

CROWDTANGLE_POST_TYPES = [
    "episode",
    "extra_clip",
    "link",
    "live_video",
    "live_video_complete",
    "live_video_scheduled",
    "native_video",
    "photo",
    "status",
    "trailer",
    "tweet",
    "video",
    "vine",
    "youtube",
]

CROWDTANGLE_SORT_TYPES = [
    "date",
    "interaction_rate",
    "overperforming",
    "total_interactions",
    "underperforming",
]

CROWDTANGLE_SUMMARY_SORT_TYPES = {"date", "subscriber_count", "total_interactions"}

CROWDTANGLE_SUMMARY_DEFAULT_SORT_TYPE = "date"

CROWDTANGLE_SEARCH_FIELDS = {
    "text_fields_and_image_text",
    "include_query_strings",
    "text_fields_only",
    "account_name_only",
    "image_text_only",
}

CROWDTANGLE_DEFAULT_SEARCH_FIELD = "text_fields_and_image_text"

CROWDTANGLE_STATISTICS = [
    "like",
    "share",
    "favorite",
    "comment",
    "love",
    "wow",
    "haha",
    "sad",
    "angry",
    "thankful",
    "care",
]

CROWDTANGLE_FULL_STATISTICS = STATISTICS = [
    ("loveCount", "love_count"),
    ("wowCount", "wow_count"),
    ("thankfulCount", "thankful_count"),
    ("interactionRate", "interaction_rate"),
    ("likeCount", "like_count"),
    ("hahaCount", "haha_count"),
    ("commentCount", "comment_count"),
    ("shareCount", "share_count"),
    ("sadCount", "sad_count"),
    ("angryCount", "angry_count"),
    ("postCount", "post_count"),
    ("totalInteractionCount", "total_interaction_count"),
    ("totalVideoTimeMS", "total_video_time_ms"),
    ("threePlusMinuteVideoCount", "three_plus_minute_video_count"),
]

CROWDTANGLE_PLATFORMS = {"facebook", "instagram", "reddit"}

CROWDTANGLE_REACTION_TYPES = [
    "angry",
    "comment",
    "haha",
    "like",
    "love",
    "sad",
    "share",
    "thankful",
    "wow",
]
