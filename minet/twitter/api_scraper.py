# =============================================================================
# Minet Twitter API Scraper
# =============================================================================
#
# Twitter public API "scraper".
#
import re
import time
import datetime
from ebbe import with_is_first
from urllib.parse import urlencode, quote
from twitwi import normalize_tweet

from minet.utils import nested_get
from minet.web import (
    create_pool,
    request,
    request_json,
    create_request_retryer
)
from minet.twitter.constants import (
    TWITTER_PUBLIC_API_DEFAULT_TIMEOUT,
    TWITTER_PUBLIC_API_AUTH_HEADER
)
from minet.twitter.exceptions import (
    TwitterGuestTokenError,
    TwitterPublicAPIRateLimitError,
    TwitterPublicAPIInvalidResponseError,
    TwitterPublicAPIParsingError,
    TwitterPublicAPIQueryTooLongError,
    TwitterPublicAPIOverCapacityError
)

# =============================================================================
# Constants
# =============================================================================
TWITTER_PUBLIC_SEARCH_ENDPOINT = 'https://api.twitter.com/2/search/adaptive.json'
MAXIMUM_QUERY_LENGTH = 500
DEFAULT_COUNT = 100
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

        if self.guest_token is None:
            self.acquire_guest_token()

        return method(self, *args, **kwargs)

    return wrapped


def create_cookie_expiration():
    return datetime.datetime.utcfromtimestamp(time.time() + 10800).strftime('%a, %d %b %Y %H:%M:%S GMT')


def forge_search_params(query, count=DEFAULT_COUNT, cursor=None):
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


CURSOR_FIRST_POSSIBLE_PATH = [
    'timeline',
    'instructions',
    0,
    'addEntries',
    'entries',
    -1,
    'content',
    'operation',
    'cursor',
    'value'
]

CURSOR_SECOND_POSSIBLE_PATH = [
    'timeline',
    'instructions',
    -1,
    'replaceEntry',
    'entry',
    'content',
    'operation',
    'cursor',
    'value'
]


def extract_cursor_from_payload(payload):
    found_cursor = nested_get(CURSOR_FIRST_POSSIBLE_PATH, payload)

    if found_cursor is None:
        found_cursor = nested_get(CURSOR_SECOND_POSSIBLE_PATH, payload)

    return found_cursor


def process_single_tweet(tweet_id, tweet_index, user_index):
    tweet = tweet_index[tweet_id]
    tweet['user'] = user_index[tweet['user_id_str']]

    # Quoted?
    quoted_id = tweet.get('quoted_status_id_str')

    # TODO: sometimes tweet is not present
    if quoted_id and quoted_id in tweet_index:
        tweet['quoted_status'] = process_single_tweet(quoted_id, tweet_index, user_index)

    # Retweeted?
    retweeted_id = tweet.get('retweeted_status_id_str')

    # TODO: sometimes tweet is not present
    if retweeted_id and retweeted_id in tweet_index:
        tweet['retweeted_status'] = process_single_tweet(retweeted_id, tweet_index, user_index)

    return tweet


def payload_tweets_iter(payload):
    tweet_index = payload['globalObjects']['tweets']
    user_index = payload['globalObjects']['users']

    for instruction in payload['timeline']['instructions']:
        if 'addEntries' in instruction:
            entries = instruction['addEntries']['entries']
        elif 'replaceEntry' in instruction:
            entries = [instruction['replaceEntry']['entry']]
        else:
            continue

        for entry in entries:
            entry_id = entry['entryId']

            # Filtering tweets
            if (
                not entry_id.startswith('sq-I-t-') and
                not entry_id.startswith('tweet-')
            ):
                continue

            tweet_meta = nested_get(['content', 'item', 'content', 'tweet'], entry)

            if tweet_meta is None:
                tweet_meta = nested_get(['content', 'item', 'content', 'tombstone', 'tweet'], entry)

            # Parsing error?
            if tweet_meta is None:
                raise TwitterPublicAPIParsingError

            # Skipping ads
            if 'promotedMetadata' in tweet_meta:
                continue

            tweet = process_single_tweet(tweet_meta['id'], tweet_index, user_index)

            # Additional metadata
            meta = None

            if tweet is not None:

                if 'forwardPivot' in tweet_meta:
                    pivot = tweet_meta['forwardPivot']

                    meta = {
                        'intervention_text': nested_get(['text', 'text'], pivot),
                        'intervention_type': pivot.get('displayType'),
                        'intervention_url': nested_get(['landingUrl', 'url'], pivot)
                    }

                yield tweet, meta


# =============================================================================
# Main class
# =============================================================================
class TwitterAPIScraper(object):
    def __init__(self):
        self.pool = create_pool(timeout=TWITTER_PUBLIC_API_DEFAULT_TIMEOUT)
        self.reset()

    def reset(self):
        self.guest_token = None
        self.cookie = None

    def request(self, url):
        return request(url, pool=self.pool, spoof_ua=True)

    def request_json(self, url, headers=None):
        return request_json(url, pool=self.pool, spoof_ua=True, headers=headers)

    def acquire_guest_token(self):
        base_url = forge_search_url('test')

        err, response = self.request(base_url)

        if err or response.status >= 400:
            raise TwitterPublicAPIInvalidResponseError

        guest_token = extract_guest_token(response.data)

        if guest_token is None:
            raise TwitterGuestTokenError

        self.guest_token = guest_token
        self.cookie = (
            response.headers['Set-Cookie'] +
            ', gt=%s; Domain=.twitter.com; Path=/; Secure ; Expires=%s' %
            (guest_token, create_cookie_expiration())
        )

    @ensure_guest_token
    def request_search(self, query, cursor=None, refs=None, dump=False):
        params = forge_search_params(query, cursor=cursor)
        url = '%s?%s' % (TWITTER_PUBLIC_SEARCH_ENDPOINT, params)

        headers = {
            'Authorization': TWITTER_PUBLIC_API_AUTH_HEADER,
            'X-Guest-Token': self.guest_token,
            'Cookie': self.cookie,
            'Accept-Language': 'en'
        }

        err, response, data = self.request_json(url, headers=headers)

        if err:
            raise err

        if response.status == 429:
            self.reset()
            raise TwitterPublicAPIRateLimitError

        if response.status >= 400:
            error = nested_get(['errors', 0], data)

            if error is not None and error.get('code') == 130:
                raise TwitterPublicAPIOverCapacityError

            raise TwitterPublicAPIInvalidResponseError

        cursor = extract_cursor_from_payload(data)
        tweets = []

        if dump:
            return data

        for tweet, meta in payload_tweets_iter(data):
            result = normalize_tweet(
                tweet,
                extract_referenced_tweets=refs is not None,
                collection_source='scraping'
            )

            if refs is not None:
                for is_first, extracted_tweet in with_is_first(result):

                    # Casting to int64 to save up memory
                    id_int64 = int(extracted_tweet['id'])

                    if id_int64 in refs:
                        continue

                    if is_first:
                        extracted_tweets.append((extracted_tweet, meta))
                    else:
                        extracted_tweets.append((extracted_tweet, None))

                    refs.add(id_int64)
            else:
                tweets.append((result, meta))

        return cursor, tweets

    def search(self, query, limit=None, before_sleep=None,
               include_referenced_tweets=False, with_meta=False):

        if len(query) > MAXIMUM_QUERY_LENGTH:
            raise TwitterPublicAPIQueryTooLongError

        cursor = None
        i = 0

        retryer = create_request_retryer(
            min=1,
            additional_exceptions=[
                TwitterPublicAPIRateLimitError,
                TwitterPublicAPIInvalidResponseError
            ],
            before_sleep=before_sleep
        )

        refs = set() if include_referenced_tweets else None

        while True:
            new_cursor, tweets = retryer(self.request_search, query, cursor, refs=refs)

            for tweet, meta in tweets:
                if with_meta:
                    yield tweet, meta

                else:
                    yield tweet

                i += 1

                if limit is not None and i >= limit:
                    return

            if new_cursor is None or len(tweets) == 0:
                return

            cursor = new_cursor
