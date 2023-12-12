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
