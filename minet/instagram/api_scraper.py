# =============================================================================
# Minet Instagram API Scraper
# =============================================================================
#
# Instagram public API "scraper".
#
import json
from json.decoder import JSONDecodeError
from urllib.parse import quote
from ebbe import getpath
import re

from minet.constants import COOKIE_BROWSERS
from minet.utils import rate_limited_method, RateLimiterState
from minet.web import (
    create_pool,
    request_json,
    grab_cookies,
    create_request_retryer,
    retrying_method,
    request_text,
)
from minet.instagram.constants import (
    INSTAGRAM_URL,
    INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT,
    INSTAGRAM_DEFAULT_THROTTLE,
)
from minet.instagram.exceptions import (
    InstagramError500,
    InstagramPublicAPIInvalidResponseError,
    InstagramInvalidCookieError,
    InstagramTooManyRequestsError,
)
from minet.instagram.formatters import format_hashtag_post, format_user_post

INSTAGRAM_GRAPHQL_ENDPOINT = "https://www.instagram.com/graphql/query/"
INSTAGRAM_HASHTAG_QUERY_HASH = "9b498c08113f1e09617a1703c22b2f32"
INSTAGRAM_MAGIC_TOKEN_PATTERN = re.compile(r"\"X-IG-App-ID\"\s*:\s*\"(\d+)\"")
INSTAGRAM_USER_ID_PATTERN = re.compile(r"\d+_(\d+)")


def forge_hashtag_search_url(name, cursor=None, count=50):
    params = {"tag_name": name, "first": count}

    if cursor is not None:
        params["after"] = cursor

    url = INSTAGRAM_GRAPHQL_ENDPOINT + "?query_hash=%s&variables=%s" % (
        INSTAGRAM_HASHTAG_QUERY_HASH,
        quote(json.dumps(params)),
    )

    return url


def forge_user_posts_url(
    name,
    count=50,
    max_id=None,
):
    if max_id is not None:
        u = INSTAGRAM_USER_ID_PATTERN.search(max_id)

        if u is not None:
            user = u.group(1)
            url = "https://i.instagram.com/api/v1/feed/user/%s/?count=%s&max_id=%s" % (
                user,
                count,
                max_id,
            )
            return url
    url = "https://i.instagram.com/api/v1/feed/user/%s/username/?count=%s" % (
        name,
        count,
    )
    return url


class InstagramAPIScraper(object):
    def __init__(self, cookie="firefox", throttle=INSTAGRAM_DEFAULT_THROTTLE):
        self.pool = create_pool(timeout=INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT)

        if cookie in COOKIE_BROWSERS:
            get_cookie_for_url = grab_cookies(cookie)
            cookie = get_cookie_for_url(INSTAGRAM_URL)

        if not cookie:
            raise InstagramInvalidCookieError

        self.cookie = cookie
        self.rate_limiter_state = RateLimiterState(1, throttle)
        self.retryer = create_request_retryer(
            min=60,
            additional_exceptions=[
                InstagramTooManyRequestsError,
                JSONDecodeError,
                InstagramError500,
            ],
        )
        self.magic_token = None

    @retrying_method()
    @rate_limited_method()
    def request_json(self, url, magic_token=False):
        headers = {"Cookie": self.cookie}
        if magic_token:
            headers["X-IG-App-ID"] = self.magic_token
        err, response, data = request_json(
            url,
            pool=self.pool,
            spoof_ua=True,
            headers=headers,
        )

        if err:
            raise err

        if response.status == 429:
            raise InstagramTooManyRequestsError

        if response.status == 500:
            raise InstagramError500

        if response.status >= 400:
            print(response.status, response.data())
            raise InstagramPublicAPIInvalidResponseError

        return data

    def get_magic_token(self):
        err, response, html = request_text("https://www.instagram.com/disney")
        if err:
            raise err

        if response.status >= 400:
            return None

        t = INSTAGRAM_MAGIC_TOKEN_PATTERN.search(html)
        if t is None:
            return None

        self.magic_token = t.group(1)
        return self.magic_token

    def ensure_magic_token(method):
        def wrapped(self, *args, **kwargs):

            if self.magic_token is None:
                self.get_magic_token()

            return method(self, *args, **kwargs)

        return wrapped

    def search_hashtag(self, hashtag):
        hashtag = hashtag.lstrip("#")
        cursor = None

        while True:
            url = forge_hashtag_search_url(hashtag, cursor=cursor)

            data = self.request_json(url)

            data = getpath(data, ["data", "hashtag", "edge_hashtag_to_media"])

            if not data:
                break

            edges = data.get("edges")

            for edge in edges:
                yield format_hashtag_post(edge["node"])

            has_next_page = getpath(data, ["page_info", "has_next_page"])

            if not has_next_page:
                break

            cursor = getpath(data, ["page_info", "end_cursor"])

    @ensure_magic_token
    def user_posts(self, name):
        name = name.lstrip("@")
        max_id = None

        while True:
            url = forge_user_posts_url(name, max_id=max_id)

            data = self.request_json(url, magic_token=True)

            if not data:
                break

            items = data.get("items")

            for item in items:
                yield format_user_post(item)

            more_available = data.get("more_available")

            if not more_available:
                break

            max_id = data.get("next_max_id")
