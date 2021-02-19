# =============================================================================
# Minet Default Values Collection
# =============================================================================
#
# Listing sane default values used throughout the whole library.
#
from urllib3 import Timeout


# Fetch-related
DEFAULT_GROUP_PARALLELISM = 1
DEFAULT_GROUP_BUFFER_SIZE = 25
DEFAULT_THROTTLE = 0.2
DEFAULT_CONNECT_TIMEOUT = 5
DEFAULT_READ_TIMEOUT = 25
DEFAULT_URLLIB3_TIMEOUT = Timeout(connect=DEFAULT_CONNECT_TIMEOUT, read=DEFAULT_READ_TIMEOUT)
DEFAULT_SPOOFED_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0'

COOKIE_BROWSERS = {
    'chrome',
    'chromium',
    'firefox',
    'opera',
    'edge'
}
