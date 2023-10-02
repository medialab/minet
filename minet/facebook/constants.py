# =============================================================================
# Minet Facebook Constants
# =============================================================================
#
# General constants used throughout the Facebook namespace.
#
from collections import OrderedDict

from minet.rate_limiting import RateLimiterState

FACEBOOK_URL = "https://www.facebook.com"
FACEBOOK_MOBILE_URL = "https://m.facebook.com"

FACEBOOK_MOBILE_DEFAULT_THROTTLE = 20.0
FACEBOOK_WEB_DEFAULT_THROTTLE = 20.0

FACEBOOK_MOBILE_RATE_LIMITER_STATE = RateLimiterState(
    1, FACEBOOK_MOBILE_DEFAULT_THROTTLE
)
FACEBOOK_WEB_RATE_LIMITER_STATE = RateLimiterState(1, FACEBOOK_WEB_DEFAULT_THROTTLE)

FACEBOOK_USER_CSV_HEADERS = ["user_label", "user_id", "user_handle", "user_url"]

FACEBOOK_COMMENT_CSV_HEADERS = [
    "post_id",
    "id",
    "user_id",
    "user_handle",
    "user_url",
    "user_label",
    "text",
    "html",
    "formatted_date",
    "date",
    "reactions",
    "replies",
    "in_reply_to",
]

FACEBOOK_POST_CSV_HEADERS = [
    "url",
    "user_id",
    "user_handle",
    "user_url",
    "user_label",
    "text",
    "html",
    "translated_text",
    "translated_html",
    "translated_from",
    "formatted_date",
    "date",
    "reactions",
    "comments",
]

FACEBOOK_POST_STATS_CSV_HEADERS = [
    "error",
    "canonical",
    "account_name",
    "timestamp",
    "time",
    "link",
    "aria_label",
    "text",
    "share_count",
    "comment_count",
    "reaction_count",
    "video_view_count",
]

FACEBOOK_REACTION_KEYS = OrderedDict(
    {
        1: "like",
        2: "love",
        3: "wow",
        4: "haha",
        7: "sad",
        8: "angry",
        11: "thankful",
        12: "pride",
        16: "care",
    }
)

FACEBOOK_POST_WITH_REACTIONS_CSV_HEADERS = FACEBOOK_POST_CSV_HEADERS + [
    "reactions_types"
]

FACEBOOK_GROUP_OR_PAGE_CSV_HEADERS = [
    "canonical_url",
    "id",
    "handle",
    "type",
    "title",
    "description",
    "profile_picture",
    "background_picture",
    "category",
    "about",
    "is_verified",
]
FACEBOOK_PAGE_CSV_HEADERS = [
    "url",
    "id",
    "handle",
    "titre",
    "description",
    "photo_profil",
    "photo_fond",
    "categorie",
    "a_propos",
    "page_verifiee",
]
