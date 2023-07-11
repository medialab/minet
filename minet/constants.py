# =============================================================================
# Minet Default Values Collection
# =============================================================================
#
# Listing sane default values used throughout the whole library.
#
from urllib3 import Timeout
from minet.user_agents.data import USER_AGENTS


# Fetch-related
DEFAULT_DOMAIN_PARALLELISM = 1
DEFAULT_IMAP_BUFFER_SIZE = 1024
DEFAULT_THROTTLE = 0.2
DEFAULT_THREADS = 25
DEFAULT_CONNECT_TIMEOUT = 5
DEFAULT_FETCH_MAX_REDIRECTS = 10
DEFAULT_RESOLVE_MAX_REDIRECTS = 20
DEFAULT_READ_TIMEOUT = 25
DEFAULT_URLLIB3_TIMEOUT = Timeout(
    connect=DEFAULT_CONNECT_TIMEOUT, read=DEFAULT_READ_TIMEOUT
)
DEFAULT_SPOOFED_UA = USER_AGENTS[0][1]
DEFAULT_SPOOFED_TLS_CIPHERS = "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA:AES256-SHA"

COOKIE_BROWSERS = {
    "chrome",
    "chromium",
    "opera",
    "opera_gx",
    "brave",
    "edge",
    "vivaldi",
    "firefox",
    "safari",
}
