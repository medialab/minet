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

TIKTOK_HTTP_API_BASE_URL = "https://open.tiktokapis.com/v2"
TIKTOK_COMMERCIAL_CONTENTS_FIELDS = (
    "id,create_timestamp,create_date,label,brand_names,creator,videos"
)
TIKTOK_COMMERCIAL_CONTENTS_MAX_COUNT = 50

TIKTOK_COMMERCIAL_CONTENTS_LABELS = {
    "1": "Paid Partnership",
    "2": "Promotional Content",
}
