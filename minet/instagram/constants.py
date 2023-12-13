# =============================================================================
# Minet Instagram Constants
# =============================================================================
#
# General constants used throughout the Instagram functions.
#
from urllib3 import Timeout

INSTAGRAM_URL = "https://www.instagram.com"
INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 2)
INSTAGRAM_MEDIA_TYPE = {1: "GraphImage", 2: "GraphVideo", 8: "GraphSidecar"}
INSTAGRAM_DEFAULT_THROTTLE = 30.0
INSTAGRAM_MAX_RANDOM_ADDENDUM = 10.0
INSTAGRAM_NB_REQUEST_LITTLE_WAIT = 10
INSTAGRAM_DEFAULT_THROTTLE_LITTLE_WAIT = 300.0
INSTAGRAM_MAX_RANDOM_ADDENDUM_LITTLE_WAIT = 300.0
INSTAGRAM_NB_REQUEST_BIG_WAIT = 2900
INSTAGRAM_DEFAULT_THROTTLE_BIG_WAIT = 1800.0
INSTAGRAM_MAX_RANDOM_ADDENDUM_BIG_WAIT = 1800.0
INSTAGRAM_MIN_TIME_RETRYER = 600.0
