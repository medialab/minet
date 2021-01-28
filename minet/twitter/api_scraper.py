# =============================================================================
# Minet Twitter API Scraper
# =============================================================================
#
# Twitter public API "scraper".
#
import re
from urllib.parse import quote

from minet.utils import create_pool, request
from minet.twitter.constants import (
    TWITTER_PUBLIC_API_DEFAULT_TIMEOUT,
    # TWITTER_PUBLIC_API_AUTH_HEADER
)
from minet.twitter.exceptions import (
    TwitterGuestTokenError
)


# =============================================================================
# Helpers
# =============================================================================
def forge_search_url(query):
    return (
        'https://twitter.com/search?f=live&type=spelling_expansion_revert_click&q=%s' %
        quote(query)
    )


GUEST_TOKEN_COOKIE_PATTERN = re.compile(rb'document\.cookie = decodeURIComponent\("gt=(\d+);')


def extract_guest_token(html):
    match = GUEST_TOKEN_COOKIE_PATTERN.search(html)

    if match is None:
        return None

    return match.group(1).decode()


# =============================================================================
# Main class
# =============================================================================
class TwitterAPIScraper(object):
    def __init__(self):
        self.http = create_pool(timeout=TWITTER_PUBLIC_API_DEFAULT_TIMEOUT)
        self.guest_token = None

    def acquire_guest_token(self):
        base_url = forge_search_url('test')

        err, response = request(self.http, base_url, spoof_ua=True)

        if err or response.status >= 400:
            raise TwitterGuestTokenError('call failed')

        guest_token = extract_guest_token(response.data)

        if guest_token is None:
            raise TwitterGuestTokenError('could not parse')

        self.guest_token = guest_token
