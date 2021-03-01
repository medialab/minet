# =============================================================================
# Minet Instagram Constants
# =============================================================================
#
# General constants used throughout the Instagram functions.
#
from urllib3 import Timeout

INSTAGRAM_URL = 'https://www.instagram.com'
INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT = Timeout(connect=10, read=60 * 2)
