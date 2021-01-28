# =============================================================================
# Minet Twitter API Scraper
# =============================================================================
#
# Twitter public API "scraper".
#
import re
import time
import datetime
from urllib.parse import urlencode, quote

from minet.utils import (
    create_pool,
    request,
    request_json
)
from minet.twitter.constants import (
    TWITTER_PUBLIC_API_DEFAULT_TIMEOUT,
    TWITTER_PUBLIC_API_AUTH_HEADER
)
from minet.twitter.exceptions import (
    TwitterGuestTokenError
)

# =============================================================================
# Constants
# =============================================================================
TWITTER_PUBLIC_SEARCH_ENDPOINT = 'https://api.twitter.com/2/search/adaptive.json'
GUEST_TOKEN_COOKIE_PATTERN = re.compile(rb'document\.cookie = decodeURIComponent\("gt=(\d+);')


# =============================================================================
# Helpers
# =============================================================================
def forge_search_url(query):
    return (
        'https://twitter.com/search?f=live&type=spelling_expansion_revert_click&q=%s' %
        quote(query)
    )


def extract_guest_token(html):
    match = GUEST_TOKEN_COOKIE_PATTERN.search(html)

    if match is None:
        return None

    return match.group(1).decode()


def ensure_guest_token(method):
    def wrapped(self, *args, **kwargs):

        # TODO: handle expiry
        if self.guest_token is None:
            self.acquire_guest_token()

        return method(self, *args, **kwargs)

    return wrapped


def create_cookie_expiration():
    return datetime.datetime.utcfromtimestamp(time.time() + 10800).strftime('%a, %d %b %Y %H:%M:%S GMT')


def forge_search_params(query, count=100, cursor=None):
    params = {
        'include_can_media_tag': '1',
        'include_ext_alt_text': 'true',
        'include_quote_count': 'true',
        'include_reply_count': '1',
        'tweet_mode': 'extended',
        'include_entities': 'true',
        'include_user_entities': 'true',
        'include_ext_media_availability': 'true',
        'send_error_codes': 'true',
        'simple_quoted_tweet': 'true',
        'spelling_corrections': '1',
        'ext': 'mediaStats,highlightedLabel',
        'tweet_search_mode': 'live',
        'count': count,
        'q': query
    }

    if cursor is not None:
        params['cursor'] = cursor

    return urlencode(params, quote_via=quote)


# =============================================================================
# Main class
# =============================================================================
class TwitterAPIScraper(object):
    def __init__(self):
        self.http = create_pool(timeout=TWITTER_PUBLIC_API_DEFAULT_TIMEOUT)
        self.guest_token = None
        self.cookie = None

    # TODO: tenacity
    def request(self, url):
        return request(self.http, url, spoof_ua=True)

    def request_json(self, url, headers=None):
        return request_json(self.http, url, spoof_ua=True, headers=headers)

    def acquire_guest_token(self):
        base_url = forge_search_url('test')

        err, response = self.request(base_url)

        if err or response.status >= 400:
            raise TwitterGuestTokenError('call failed')

        guest_token = extract_guest_token(response.data)

        if guest_token is None:
            raise TwitterGuestTokenError('could not parse')

        self.guest_token = guest_token
        self.cookie = (
            response.headers['Set-Cookie'] +
            ', gt=%s; Domain=.twitter.com; Path=/; Secure ; Expires=%s' %
            (guest_token, create_cookie_expiration())
        )

    @ensure_guest_token
    def request_search(self, query):
        params = forge_search_params(query)
        url = '%s?%s' % (TWITTER_PUBLIC_SEARCH_ENDPOINT, params)

        headers = {
            'Authorization': TWITTER_PUBLIC_API_AUTH_HEADER,
            'X-Guest-Token': self.guest_token,
            'Cookie': self.cookie
        }

        err, response, data = self.request_json(url, headers=headers)

        print(err)
        print(response.status)
        print(data)
