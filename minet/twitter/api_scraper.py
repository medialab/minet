# =============================================================================
# Minet Twitter API Scraper
# =============================================================================
#
# Twitter public API "scraper".
#
import time
import datetime
from urllib.parse import urlencode, quote
from twitwi import normalize_tweet
from ebbe import with_is_first, getpath, pathgetter
from json import JSONDecodeError
from tenacity import RetryCallState

from minet.web import (
    create_pool_manager,
    request,
    create_request_retryer,
    retrying_method,
)
from minet.cookies import (
    coerce_cookie_for_url_from_browser,
    get_cookie_morsel_value,
    cookie_string_to_dict,
)
from minet.rate_limiting import RateLimiterState, rate_limited_method
from minet.twitter.constants import (
    TWITTER_PUBLIC_API_DEFAULT_TIMEOUT,
    TWITTER_PUBLIC_API_AUTH_HEADER,
)
from minet.twitter.exceptions import (
    # TwitterPublicAPIGuestTokenError,
    TwitterPublicAPIBadRequest,
    TwitterPublicAPIRateLimitError,
    TwitterPublicAPIInvalidResponseError,
    TwitterPublicAPIParsingError,
    TwitterPublicAPIQueryTooLongError,
    TwitterPublicAPIOverCapacityError,
    TwitterPublicAPIHiccupError,
    TwitterPublicAPIncompleteTweetIndexError,
    TwitterPublicAPIncompleteUserIndexError,
    TwitterPublicAPIInvalidCookieError,
    TwitterPublicAPIBadAuthError,
    TwitterPublicAPINotWorkingAnymore,
)

# =============================================================================
# Constants
# =============================================================================
TWITTER_PUBLIC_SEARCH_ENDPOINT = "https://api.twitter.com/2/search/adaptive.json"
TWITTER_GUEST_ACTIVATE_ENDPOINT = "https://api.twitter.com/1.1/guest/activate.json"
MAXIMUM_QUERY_LENGTH = 500
DEFAULT_COUNT = 100  # NOTE: the actual upper limit seems to be 20, but I keep 100 just in case it changes in the future, who knows...
MAX_GUEST_TOKEN_USE_COUNT = 100


# =============================================================================
# Helpers
# =============================================================================
def is_query_too_long(query):
    return len(quote(query)) > MAXIMUM_QUERY_LENGTH


def is_cookie_valid(cookie: str) -> bool:
    dict_cookie = cookie_string_to_dict(cookie)

    return bool(
        dict_cookie.get("guest_id")
        and dict_cookie.get("ct0")
        and dict_cookie.get("auth_token")
    )


# def ensure_guest_token(method):
#     def wrapped(self: "TwitterAPIScraper", *args, **kwargs):

#         # NOTE: we refresh the guest token periodically to avoid
#         # losing time wrt failed request after expiration
#         if (
#             self.guest_token is None
#             or self.guest_token_use_count >= MAX_GUEST_TOKEN_USE_COUNT
#         ):
#             self.acquire_guest_token()
#             self.guest_token_use_count = 0

#         self.guest_token_use_count += 1
#         return method(self, *args, **kwargs)

#     return wrapped


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

CURSOR_THIRD_POSSIBLE_PATH_GETTER = pathgetter(
    [
        "data",
        "search_by_raw_query",
        "search_timeline",
        "timeline",
        "instructions",
        0,
        "entries",
        -1,
        "content",
        "value",
    ]
)

CURSOR_FOURTH_POSSIBLE_PATH_GETTER = pathgetter(
    [
        "data",
        "search_by_raw_query",
        "search_timeline",
        "timeline",
        "instructions",
        -1,
        "entry",
        "content",
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

    if found_cursor is None:
        found_cursor = CURSOR_THIRD_POSSIBLE_PATH_GETTER(payload)

    if found_cursor is None:
        found_cursor = CURSOR_FOURTH_POSSIBLE_PATH_GETTER(payload)

    return found_cursor


def extract_cursor_from_users_payload(payload):
    return CURSOR_USER_PATH_GETTER(payload)


def process_single_tweet(tweet_id, tweet_index, user_index):
    try:
        tweet = tweet_index[tweet_id]
    except KeyError:
        raise TwitterPublicAPIncompleteTweetIndexError(
            tweet_id=tweet_id, tweet_index=tweet_index
        )

    try:
        tweet["user"] = user_index[tweet["user_id_str"]]
    except KeyError:
        raise TwitterPublicAPIncompleteUserIndexError(
            user_id=tweet["user_id_str"], user_index=user_index
        )

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
    instructions = payload["data"]["search_by_raw_query"]["search_timeline"][
        "timeline"
    ]["instructions"]

    tweet_index = None
    user_index = None

    # with open("dump.json", "w") as f:
    #     import json

    #     json.dump(payload, f, ensure_ascii=False, indent=2)

    for instruction in instructions:
        if instruction["type"] == "TimelineAddEntries":
            entries = instruction["entries"]
        elif instruction["type"] == "TimelineReplaceEntry":
            entries = [instruction["entry"]]
        else:
            continue

        for entry in entries:
            entry_id = entry["entryId"]

            # Filtering tweets
            if not entry_id.startswith("sq-I-t-") and not entry_id.startswith("tweet-"):
                continue

            tweet_root = getpath(
                entry, ["content", "itemContent", "tweet_results", "result"]
            )

            # Parsing error?
            # NOTE: new API is inconsistent and returns empty objects...
            if tweet_root is None:
                continue
                # raise TwitterPublicAPIParsingError

            if tweet_root["__typename"] == "TweetWithVisibilityResults":
                tweet_root = tweet_root["tweet"]

            try:
                tweet_meta = tweet_root["legacy"]
            except KeyError:
                raise TwitterPublicAPIParsingError(entry_id)

            tweet_meta["source"] = tweet_root["source"]

            # NOTE: tombstone not working anymore
            # if tweet_meta is None:
            #     tweet_meta = getpath(
            #         entry, ["content", "item", "content", "tombstone", "tweet"]
            #     )

            # Skipping ads
            if "promotedMetadata" in tweet_meta:
                continue

            # NOTE: with new API results we need to build this index each time
            tweet_index = {tweet_meta["id_str"]: tweet_meta}
            user_index = {}

            # Tweet user
            user_index[tweet_meta["user_id_str"]] = tweet_root["core"]["user_results"][
                "result"
            ]["legacy"]

            # Quote
            quoted_root = getpath(tweet_root, ["quoted_status_result", "result"])

            if quoted_root is not None:
                if quoted_root["__typename"] == "TweetWithVisibilityResults":
                    quoted_root = quoted_root["tweet"]

                quoted_meta = quoted_root["legacy"]
                quoted_meta["source"] = quoted_root["source"]
                tweet_index[quoted_meta["id_str"]] = quoted_meta
                user_index[quoted_meta["user_id_str"]] = quoted_root["core"][
                    "user_results"
                ]["result"]["legacy"]

            for user_str_id, user_meta in user_index.items():
                user_meta["id_str"] = user_str_id

            tweet = process_single_tweet(tweet_meta["id_str"], tweet_index, user_index)

            # Additional metadata
            # NOTE: not working anymore
            meta = None

            if tweet is not None:
                # if "forwardPivot" in tweet_meta:
                #     pivot = tweet_meta["forwardPivot"]

                #     meta = {
                #         "intervention_text": getpath(pivot, ["text", "text"]),
                #         "intervention_type": pivot.get("displayType"),
                #         "intervention_url": getpath(pivot, ["landingUrl", "url"]),
                #     }

                yield tweet, meta


# =============================================================================
# Main class
# =============================================================================
class TwitterAPIScraper(object):
    def __init__(self, cookie: str):
        self.pool_manager = create_pool_manager(
            timeout=TWITTER_PUBLIC_API_DEFAULT_TIMEOUT, spoof_tls_ciphers=True
        )

        # NOTE: expressed as number of calls (returning ~20 tweets) per seconds
        self.rate_limiter_state = RateLimiterState(25, 60)

        # self.reset()

        # NOTE: since 2023-04-21, Twitter search is not available anymore
        # if you are not logged in to the website. This means that the old
        # method of acquiring and rotating a guest token is now moot.
        # An alternative is therefore to rely on the user's cookie to
        # spoof the connection and scrape the search as before.
        #
        # The issue here is that Twitter knows who you are and I strongly
        # expect them to kick accounts scraping in the near future as it
        # would be quite easy to do so.
        #
        # They might also very well limit the number of search result
        # returned to prevent scraping altogether, connected or not.
        self.cookie = coerce_cookie_for_url_from_browser(
            cookie, TWITTER_PUBLIC_SEARCH_ENDPOINT
        )

        if not is_cookie_valid(self.cookie):
            raise TwitterPublicAPIInvalidCookieError

        self.csrf_token = get_cookie_morsel_value(self.cookie, "ct0")

        def epilog_builder(retry_state: RetryCallState):
            exc = retry_state.outcome.exception()

            if hasattr(exc, "format_epilog") and callable(exc.format_epilog):
                return exc.format_epilog()

            return None

        self.retryer = create_request_retryer(
            min=1,
            additional_exceptions=[
                TwitterPublicAPIRateLimitError,
                TwitterPublicAPIInvalidResponseError,
                TwitterPublicAPIOverCapacityError,
                TwitterPublicAPIncompleteTweetIndexError,
                TwitterPublicAPIncompleteUserIndexError,
                TwitterPublicAPIHiccupError,  # TODO: I might want to drop this at some point
            ],
            epilog=epilog_builder,
        )

    # def reset(self):
    #     self.guest_token = None
    #     self.guest_token_use_count = 0
    #     self.cookie = None

    @rate_limited_method()
    def request(self, url, headers=None, method="GET"):
        return request(
            url,
            pool_manager=self.pool_manager,
            spoof_ua=True,
            method=method,
            headers=headers,
        )

    # def acquire_guest_token(self):
    #     headers = {
    #         "Authorization": TWITTER_PUBLIC_API_AUTH_HEADER,
    #         "Accept-Language": "en-US,en;q=0.5",
    #     }

    #     response = self.request(TWITTER_GUEST_ACTIVATE_ENDPOINT, headers, method="POST")

    #     if response.status >= 400:
    #         raise TwitterPublicAPIInvalidResponseError(
    #             status=response.status, response_text=response.text
    #         )

    #     try:
    #         api_token_response = response.json()
    #     except JSONDecodeError:
    #         raise TwitterPublicAPIInvalidResponseError(
    #             status=response.status, response_text=response.text
    #         )

    #     guest_token = api_token_response.get("guest_token")

    #     if guest_token is None:
    #         raise TwitterPublicAPIGuestTokenError

    #     self.guest_token = guest_token
    #     self.cookie = response.headers[
    #         "Set-Cookie"
    #     ] + ", gt=%s; Domain=.twitter.com; Path=/; Secure ; Expires=%s" % (
    #         guest_token,
    #         create_cookie_expiration(),
    #     )

    # @ensure_guest_token
    def request_search(self, url):
        headers = {
            "Authorization": TWITTER_PUBLIC_API_AUTH_HEADER,
            # "X-Guest-Token": self.guest_token,
            "Cookie": self.cookie,
            "Accept-Language": "en-US,en;q=0.5",
            "X-Csrf-Token": self.csrf_token,
            "X-Twitter-Active-User": "yes",
            "X-Twitter-Auth-Type": "OAuth2Session",
            "X-Twitter-Client-Language": "en",
        }

        response = self.request(url, headers=headers)

        if response.status == 429:
            # self.reset()
            raise TwitterPublicAPIRateLimitError

        if response.status in [401, 403]:
            # self.reset()
            raise TwitterPublicAPIBadAuthError(response.status)

        try:
            data = response.json()
        except JSONDecodeError:
            raise TwitterPublicAPIInvalidResponseError(
                status=response.status, response_text=response.text
            )

        if response.status >= 400:
            error = getpath(data, ["errors", 0])

            if error is not None and response.status == 400 and error.get("code") == 47:
                raise TwitterPublicAPIBadRequest

            if error is not None and error.get("code") == 130:
                raise TwitterPublicAPIOverCapacityError

            raise TwitterPublicAPIInvalidResponseError(
                status=response.status, response_text=response.text
            )

        return data

    @retrying_method()
    def request_tweet_search(self, query, locale, cursor=None, refs=None, dump=False):
        # TODO: refactor lol
        url = "https://twitter.com/i/api/graphql/L1VfBERtzc3VkBBT0YAYHA/SearchTimeline?variables=%7B%22rawQuery%22%3A%22{}%22%2C%22count%22%3A20%2C%22querySource%22%3A%22typed_query%22%2C%22product%22%3A%22Latest%22%7D&features=%7B%22rweb_lists_timeline_redesign_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Afalse%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_media_download_video_enabled%22%3Afalse%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D&fieldToggles=%7B%22withArticleRichContentState%22%3Afalse%7D".format(
            quote(query)
        )

        if cursor is not None:
            url = "https://twitter.com/i/api/graphql/L1VfBERtzc3VkBBT0YAYHA/SearchTimeline?variables=%7B%22rawQuery%22%3A%22{}%22%2C%22count%22%3A20%2C%22cursor%22%3A%22{}%22%2C%22querySource%22%3A%22typed_query%22%2C%22product%22%3A%22Latest%22%7D&features=%7B%22rweb_lists_timeline_redesign_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22responsive_web_twitter_article_tweet_consumption_enabled%22%3Afalse%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Atrue%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Atrue%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22longform_notetweets_inline_media_enabled%22%3Atrue%2C%22responsive_web_media_download_video_enabled%22%3Afalse%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D&fieldToggles=%7B%22withArticleRichContentState%22%3Afalse%7D".format(
                quote(query), quote(cursor)
            )

        # NOTE: old method
        # params = forge_search_params(query, cursor=cursor, target="tweets")
        # url = "%s?%s" % (TWITTER_PUBLIC_SEARCH_ENDPOINT, params)

        data = self.request_search(url)

        next_cursor = extract_cursor_from_tweets_payload(data)

        tweets = []

        if dump:
            return data

        for tweet, meta in tweets_payload_iter(data):
            try:
                result = normalize_tweet(
                    tweet,
                    locale=locale,
                    extract_referenced_tweets=refs is not None,
                    collection_source="scraping",
                )
            except Exception:
                raise TwitterPublicAPIParsingError(tweet["id_str"])

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

    @retrying_method()
    def request_user_search(self, query, locale, cursor=None, dump=False):
        raise TwitterPublicAPINotWorkingAnymore
        # params = forge_search_params(query, cursor=cursor, target="users")
        # url = "%s?%s" % (TWITTER_PUBLIC_SEARCH_ENDPOINT, params)

        # data = self.request_search(url)

        # next_cursor = extract_cursor_from_users_payload(data)

        # if dump:
        #     return data

        # users = [
        #     normalize_user(user, locale=locale)
        #     for user in data["globalObjects"]["users"].values()
        # ]

        # return next_cursor, users

    def search_tweets(
        self,
        query,
        locale=None,
        limit=None,
        include_referenced_tweets=False,
        with_meta=False,
    ):
        if is_query_too_long(query):
            raise TwitterPublicAPIQueryTooLongError

        cursor = None
        i = 0

        refs = set() if include_referenced_tweets else None

        while True:
            new_cursor, tweets = self.request_tweet_search(
                query, locale, cursor, refs=refs
            )

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

    def search_users(self, query, locale=None, limit=None):
        if is_query_too_long(query):
            raise TwitterPublicAPIQueryTooLongError

        cursor = None
        i = 0

        while True:
            new_cursor, users = self.request_user_search(query, locale, cursor)

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
