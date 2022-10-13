# =============================================================================
# Minet Instagram API Scraper
# =============================================================================
#
# Instagram public API "scraper".
#
import json
from urllib.parse import quote
from ebbe import getpath
import re

from minet.constants import COOKIE_BROWSERS
from minet.utils import sleep_with_entropy
from minet.web import (
    create_pool,
    create_request_retryer,
    request_json,
    grab_cookies,
    request_text,
    retrying_method,
)
from minet.instagram.constants import (
    INSTAGRAM_DEFAULT_THROTTLE_EVERY_10_CALLS,
    INSTAGRAM_MAX_RANDOM_ADDENDUM,
    INSTAGRAM_MAX_RANDOM_ADDENDUM_EVERY_10_CALLS,
    INSTAGRAM_MIN_TIME_RETRYER,
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
from minet.instagram.formatters import (
    format_hashtag_post,
    format_user_follow,
    format_user_post,
)

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


def forge_user_url(name):
    url = "https://i.instagram.com/api/v1/users/web_profile_info/?username=%s" % name

    return url


def forge_user_followers_url(
    id,
    count=50,
    max_id=None,
):
    url = (
        "https://i.instagram.com/api/v1/friendships/%s/followers/?count=%s&search_surface=follow_list_page"
        % (
            id,
            count,
        )
    )
    if max_id:
        url += "&max_id=%s" % max_id

    return url


def forge_user_following_url(
    id,
    count=50,
    max_id=None,
):
    url = (
        "https://i.instagram.com/api/v1/friendships/%s/following/?count=%s&search_surface=follow_list_page"
        % (
            id,
            count,
        )
    )
    if max_id:
        url += "&max_id=%s" % max_id

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
    def __init__(self, cookie="firefox"):
        self.pool = create_pool(timeout=INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT)

        if cookie in COOKIE_BROWSERS:
            get_cookie_for_url = grab_cookies(cookie)
            cookie = get_cookie_for_url(INSTAGRAM_URL)

        if not cookie:
            raise InstagramInvalidCookieError

        self.cookie = cookie
        self.magic_token = None
        self.nb_tries = 0
        self.retryer = create_request_retryer(
            min=INSTAGRAM_MIN_TIME_RETRYER,
            additional_exceptions=[InstagramTooManyRequestsError, InstagramError500],
        )

    @retrying_method()
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
            print(response.status, response.data)
            raise InstagramPublicAPIInvalidResponseError

        if self.nb_tries == 10:
            sleep_with_entropy(
                INSTAGRAM_DEFAULT_THROTTLE_EVERY_10_CALLS,
                INSTAGRAM_MAX_RANDOM_ADDENDUM_EVERY_10_CALLS,
            )
            self.nb_tries = 0

            return data

        sleep_with_entropy(INSTAGRAM_DEFAULT_THROTTLE, INSTAGRAM_MAX_RANDOM_ADDENDUM)
        self.nb_tries += 1

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
    def get_user_id(self, name):
        name = name.lstrip("@")

        url = forge_user_url(name)

        data = self.request_json(url, magic_token=True)

        user_id = getpath(data, ["data", "user", "id"])

        return user_id

    @ensure_magic_token
    def user_followers(self, name):
        name = name.lstrip("@")
        id = self.get_user_id(name)
        max_id = None

        while True:
            url = forge_user_followers_url(id, max_id=max_id)

            data = self.request_json(url, magic_token=True)

            items = data.get("users")

            if not data:
                break

            for item in items:
                yield format_user_follow(item)

            max_id = data.get("next_max_id")

            if not max_id:
                break

    @ensure_magic_token
    def user_following(self, name):
        name = name.lstrip("@")
        id = self.get_user_id(name)
        max_id = None

        while True:
            url = forge_user_following_url(id, max_id=max_id)

            data = self.request_json(url, magic_token=True)

            items = data.get("users")

            if not data:
                break

            for item in items:
                yield format_user_follow(item)

            max_id = data.get("next_max_id")

            if not max_id:
                break

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
