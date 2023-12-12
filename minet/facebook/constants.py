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

FACEBOOK_MOBILE_DEFAULT_THROTTLE = 2.0
FACEBOOK_WEB_DEFAULT_THROTTLE = 20.0

FACEBOOK_MOBILE_RATE_LIMITER_STATE = RateLimiterState(
    1, FACEBOOK_MOBILE_DEFAULT_THROTTLE
)
FACEBOOK_WEB_RATE_LIMITER_STATE = RateLimiterState(1, FACEBOOK_WEB_DEFAULT_THROTTLE)

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
