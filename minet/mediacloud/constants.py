# =============================================================================
# Minet Mediacloud Constants
# =============================================================================
#
# Bunch of mediacloud-related constants.
#
from urllib3 import Timeout

MEDIACLOUD_API_BASE_URL = "https://api.mediacloud.org/api/v2"
MEDIACLOUD_DEFAULT_TIMEOUT = Timeout(connect=30, read=60 * 5)
MEDIACLOUD_DEFAULT_BATCH = 250
