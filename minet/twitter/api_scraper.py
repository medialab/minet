# =============================================================================
# Minet Twitter API Scraper
# =============================================================================
#
# Twitter public API "scraper".
#
import time
import datetime
from ebbe import with_is_first
from urllib.parse import urlencode, quote
from twitwi import normalize_tweet, normalize_user
from ebbe import getpath, pathgetter

from minet.web import (
    create_pool,
    request,
    request_json,
    create_request_retryer,
    retrying_method,
)
from minet.twitter.constants import (
    TWITTER_PUBLIC_API_DEFAULT_TIMEOUT,
    TWITTER_PUBLIC_API_AUTH_HEADER,
)
from minet.twitter.exceptions import (
    TwitterGuestTokenError,
    TwitterPublicAPIBadRequest,
    TwitterPublicAPIRateLimitError,
    TwitterPublicAPIInvalidResponseError,
    TwitterPublicAPIParsingError,
    TwitterPublicAPIQueryTooLongError,
    TwitterPublicAPIOverCapacityError,
    TwitterPublicAPIHiccupError,
)

# =============================================================================
# Constants
# =============================================================================
TWITTER_PUBLIC_SEARCH_ENDPOINT = "https://api.twitter.com/2/search/adaptive.json"
TWITTER_GUEST_ACTIVATE_ENDPOINT = "https://api.twitter.com/1.1/guest/activate.json"
MAXIMUM_QUERY_LENGTH = 500
DEFAULT_COUNT = 100  # NOTE: the actual upper limit seems to be 20, but I keep 100 just in case it changes in the future, who knows...


# =============================================================================
# Helpers
# =============================================================================
def is_query_too_long(query):
    return len(quote(query)) > MAXIMUM_QUERY_LENGTH


def ensure_guest_token(method):
    def wrapped(self, *args, **kwargs):

        if self.guest_token is None:
            self.acquire_guest_token()

        return method(self, *args, **kwargs)

    return wrapped


def create_cookie_expiration():
    return datetime.datetime.utcfromtimestamp(time.time() + 10800).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )


TWEET_SEARCH_DEFAULT_PARAMS = {
    "include_profile_interstitial_type": "1",
    "include_blocking": "1",
    "include_blocked_by": "1",
    "include_followed_by": "1",
    "include_want_retweets": "1",
    "include_mute_edge": "1",
    "include_can_dm": "1",
    "include_can_media_tag": "1",
    "include_ext_has_nft_avatar": "1",
    "include_ext_is_blue_verified": "1",
    "include_ext_verified_type": "1",
    "skip_status": "1",
    "cards_platform": "Web-12",
    "include_cards": "1",
    "include_ext_alt_text": "true",
    "include_ext_limited_action_results": "false",
    "include_quote_count": "true",
    "include_reply_count": "1",
    "tweet_mode": "extended",
    "include_ext_collab_control": "true",
    "include_ext_views": "true",
    "include_entities": "true",
    "include_user_entities": "true",
    "include_ext_media_color": "true",
    "include_ext_media_availability": "true",
    "include_ext_sensitive_media_warning": "true",
    "include_ext_trusted_friends_metadata": "true",
    "send_error_codes": "true",
    "simple_quoted_tweet": "true",
    "tweet_search_mode": "live",
    "query_source": "spelling_expansion_revert_click",
    "pc": "1",
    "spelling_corrections": "1",
    "include_ext_edit_control": "true",
    "ext": "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata,unmentionInfo,editControl,collab_control,vibe",
}

USER_SEARCH_DEFAULT_PARAMS = {
    "include_profile_interstitial_type": "1",
    "include_blocking": "1",
    "include_blocked_by": "1",
    "include_followed_by": "1",
    "include_want_retweets": "1",
    "include_mute_edge": "1",
    "include_can_dm": "1",
    "include_can_media_tag": "1",
    "include_ext_has_nft_avatar": "1",
    "skip_status": "1",
    "cards_platform": "Web-12",
    "include_cards": "1",
    "include_ext_alt_text": "true",
    "include_quote_count": "true",
    "include_reply_count": "1",
    "tweet_mode": "extended",
    "include_entities": "true",
    "include_user_entities": "true",
    "include_ext_media_color": "true",
    "include_ext_media_availability": "true",
    "include_ext_sensitive_media_warning": "true",
    "send_error_codes": "true",
    "simple_quoted_tweet": "true",
    "result_filter": "user",
    "query_source": "typed_query",
    "pc": "1",
    "spelling_corrections": "0",
    "ext": "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,superFollowMetadata",
}


def forge_search_params(query, target="tweets", count=DEFAULT_COUNT, cursor=None):
    if target == "tweets":
        base = TWEET_SEARCH_DEFAULT_PARAMS
    elif target == "users":
        base = USER_SEARCH_DEFAULT_PARAMS
    else:
        raise TypeError('Invalid target. Expecting "tweets" or "users".')

    params = {**base, "q": query, "count": count}

    if cursor is not None:
        params["cursor"] = cursor

    return urlencode(params, quote_via=quote)


CURSOR_FIRST_POSSIBLE_PATH_GETTER = pathgetter(
    [
        "timeline",
        "instructions",
        0,
        "addEntries",
        "entries",
        -1,
        "content",
        "operation",
        "cursor",
        "value",
    ]
)

CURSOR_SECOND_POSSIBLE_PATH_GETTER = pathgetter(
    [
        "timeline",
        "instructions",
        -1,
        "replaceEntry",
        "entry",
        "content",
        "operation",
        "cursor",
        "value",
    ]
)

CURSOR_USER_PATH_GETTER = pathgetter(
    [
        "timeline",
        "instructions",
        -1,
        "addEntries",
        "entries",
        -1,
        "content",
        "operation",
        "cursor",
        "value",
    ]
)


def extract_cursor_from_tweets_payload(payload):
    found_cursor = CURSOR_FIRST_POSSIBLE_PATH_GETTER(payload)

    if found_cursor is None:
        found_cursor = CURSOR_SECOND_POSSIBLE_PATH_GETTER(payload)

    return found_cursor


def extract_cursor_from_users_payload(payload):
    return CURSOR_USER_PATH_GETTER(payload)


def process_single_tweet(tweet_id, tweet_index, user_index):
    tweet = tweet_index[tweet_id]
    tweet["user"] = user_index[tweet["user_id_str"]]

    # Quoted?
    quoted_id = tweet.get("quoted_status_id_str")

    # TODO: sometimes tweet is not present
    if quoted_id and quoted_id in tweet_index:
        tweet["quoted_status"] = process_single_tweet(
            quoted_id, tweet_index, user_index
        )

    # Retweeted?
    retweeted_id = tweet.get("retweeted_status_id_str")

    # TODO: sometimes tweet is not present
    if retweeted_id and retweeted_id in tweet_index:
        tweet["retweeted_status"] = process_single_tweet(
            retweeted_id, tweet_index, user_index
        )

    return tweet


def tweets_payload_iter(payload):
    tweet_index = payload["globalObjects"]["tweets"]
    user_index = payload["globalObjects"]["users"]

    for instruction in payload["timeline"]["instructions"]:
        if "addEntries" in instruction:
            entries = instruction["addEntries"]["entries"]
        elif "replaceEntry" in instruction:
            entries = [instruction["replaceEntry"]["entry"]]
        else:
            continue

        for entry in entries:
            entry_id = entry["entryId"]

            # Filtering tweets
            if not entry_id.startswith("sq-I-t-") and not entry_id.startswith("tweet-"):
                continue

            tweet_meta = getpath(entry, ["content", "item", "content", "tweet"])

            if tweet_meta is None:
                tweet_meta = getpath(
                    entry, ["content", "item", "content", "tombstone", "tweet"]
                )

            # Parsing error?
            if tweet_meta is None:
                raise TwitterPublicAPIParsingError

            # Skipping ads
            if "promotedMetadata" in tweet_meta:
                continue

            tweet = process_single_tweet(tweet_meta["id"], tweet_index, user_index)

            # Additional metadata
            meta = None

            if tweet is not None:

                if "forwardPivot" in tweet_meta:
                    pivot = tweet_meta["forwardPivot"]

                    meta = {
                        "intervention_text": getpath(pivot, ["text", "text"]),
                        "intervention_type": pivot.get("displayType"),
                        "intervention_url": getpath(pivot, ["landingUrl", "url"]),
                    }

                yield tweet, meta


# =============================================================================
# Main class
# =============================================================================
class TwitterAPIScraper(object):
    def __init__(self):
        self.pool = create_pool(
            timeout=TWITTER_PUBLIC_API_DEFAULT_TIMEOUT, spoof_tls_ciphers=True
        )
        self.reset()

        self.retryer = create_request_retryer(
            min=1,
            additional_exceptions=[
                TwitterPublicAPIRateLimitError,
                TwitterPublicAPIInvalidResponseError,
                TwitterPublicAPIHiccupError,  # TODO: I might want to drop this at some point
            ],
        )

    def reset(self):
        self.guest_token = None
        self.cookie = None

    def request(self, url):
        return request(url, pool=self.pool, spoof_ua=True)

    def request_json(self, url, headers=None, method="GET"):
        return request_json(
            url, pool=self.pool, spoof_ua=True, method=method, headers=headers
        )

    def acquire_guest_token(self):
        headers = {
            "Authorization": TWITTER_PUBLIC_API_AUTH_HEADER,
            "Accept-Language": "en-US,en;q=0.5",
        }

        err, response, api_token_response = self.request_json(
            TWITTER_GUEST_ACTIVATE_ENDPOINT, headers, method="POST"
        )

        if err or response.status >= 400:
            raise TwitterPublicAPIInvalidResponseError

        guest_token = api_token_response.get("guest_token")
        if guest_token is None:
            raise TwitterGuestTokenError

        self.guest_token = guest_token
        self.cookie = response.headers[
            "Set-Cookie"
        ] + ", gt=%s; Domain=.twitter.com; Path=/; Secure ; Expires=%s" % (
            guest_token,
            create_cookie_expiration(),
        )

    @retrying_method()
    @ensure_guest_token
    def request_search(self, url):
        headers = {
            "Authorization": TWITTER_PUBLIC_API_AUTH_HEADER,
            "X-Guest-Token": self.guest_token,
            "Cookie": self.cookie,
            "Accept-Language": "en-US,en;q=0.5",
        }

        err, response, data = self.request_json(url, headers=headers)

        if err:
            raise err

        if response.status in [403, 429]:
            self.reset()
            raise TwitterPublicAPIRateLimitError

        if response.status >= 400:
            error = getpath(data, ["errors", 0])

            if error is not None and response.status == 400 and error.get("code") == 47:
                raise TwitterPublicAPIBadRequest

            if error is not None and error.get("code") == 130:
                raise TwitterPublicAPIOverCapacityError

            raise TwitterPublicAPIInvalidResponseError

        return data

    def request_tweet_search(self, query, cursor=None, refs=None, dump=False):
        params = forge_search_params(query, cursor=cursor, target="tweets")
        url = "%s?%s" % (TWITTER_PUBLIC_SEARCH_ENDPOINT, params)

        data = self.request_search(url)

        next_cursor = extract_cursor_from_tweets_payload(data)
        tweets = []

        if dump:
            return data

        for tweet, meta in tweets_payload_iter(data):
            result = normalize_tweet(
                tweet,
                extract_referenced_tweets=refs is not None,
                collection_source="scraping",
            )

            if refs is not None:
                for is_first, extracted_tweet in with_is_first(result):

                    # Casting to int64 to save up memory
                    id_int64 = int(extracted_tweet["id"])

                    if id_int64 in refs:
                        continue

                    if is_first:
                        tweets.append((extracted_tweet, meta))
                    else:
                        tweets.append((extracted_tweet, None))

                    refs.add(id_int64)
            else:
                tweets.append((result, meta))

        # Attempting to fix Twitter's public-facing API recent hiccups (#316):
        # It seems that sometimes the API returns an empty response, containing
        # the same cursor as before, in which case we should retry...
        # NOTE: in fact, the real issue lies elsewhere as the way to hit the API
        # changed slightly and was causing our issues. But we cannot rely
        # on this condition now because it will degenerate to a retry loop
        # when hitting the last available tweets of the query.
        # NOTE: since those API changes, we cannot get 100 results at once anymore
        # as the upper limit seems to be 20 now :'(

        # if not tweets and cursor == next_cursor:
        #     raise TwitterPublicAPIHiccupError

        return next_cursor, tweets

    def request_user_search(self, query, cursor=None, dump=False):
        params = forge_search_params(query, cursor=cursor, target="users")
        url = "%s?%s" % (TWITTER_PUBLIC_SEARCH_ENDPOINT, params)

        data = self.request_search(url)

        next_cursor = extract_cursor_from_users_payload(data)

        if dump:
            return data

        users = [
            normalize_user(user) for user in data["globalObjects"]["users"].values()
        ]

        return next_cursor, users

    def search_tweets(
        self, query, limit=None, include_referenced_tweets=False, with_meta=False
    ):

        if is_query_too_long(query):
            raise TwitterPublicAPIQueryTooLongError

        cursor = None
        i = 0

        refs = set() if include_referenced_tweets else None

        while True:
            new_cursor, tweets = self.request_tweet_search(query, cursor, refs=refs)

            for tweet, meta in tweets:
                if with_meta:
                    yield tweet, meta

                else:
                    yield tweet

                i += 1

                if limit is not None and i >= limit:
                    return

            # NOTE: we cannot stop when no tweets are found anymore because
            # of Twitter's public facing API's strange hiccups.
            # Comparing cursors seems to be the only good option now...
            if new_cursor is None or new_cursor == cursor:
                return

            cursor = new_cursor

    def search_users(self, query, limit=None):
        if is_query_too_long(query):
            raise TwitterPublicAPIQueryTooLongError

        cursor = None
        i = 0

        while True:
            new_cursor, users = self.request_user_search(query, cursor)

            if not users:
                return

            for user in users:
                yield user

                i += 1

                if limit is not None and i >= limit:
                    return

            if new_cursor is None or new_cursor == cursor:
                return

            cursor = new_cursor
