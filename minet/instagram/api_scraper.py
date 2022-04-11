# =============================================================================
# Minet Instagram API Scraper
# =============================================================================
#
# Instagram public API "scraper".
#
import json
from urllib.parse import quote
from ebbe import getpath

from minet.constants import COOKIE_BROWSERS
from minet.web import create_pool, request_json, grab_cookies
from minet.instagram.constants import (
    INSTAGRAM_URL,
    INSTAGRAM_PUBLIC_API_DEFAULT_TIMEOUT,
)
from minet.instagram.exceptions import (
    InstagramPublicAPIInvalidResponseError,
    InstagramInvalidCookieError,
)

INSTAGRAM_GRAPHQL_ENDPOINT = "https://www.instagram.com/graphql/query/"
INSTAGRAM_HASHTAG_QUERY_HASH = "9b498c08113f1e09617a1703c22b2f32"


def forge_hashtag_search_url(name, cursor=None, count=50):
    params = {"tag_name": name, "first": count}

    if cursor is not None:
        params["after"] = cursor

    url = INSTAGRAM_GRAPHQL_ENDPOINT + "?query_hash=%s&variables=%s" % (
        INSTAGRAM_HASHTAG_QUERY_HASH,
        quote(json.dumps(params)),
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

    def request_json(self, url):
        err, response, data = request_json(
            url, pool=self.pool, spoof_ua=True, headers={"Cookie": self.cookie}
        )

        if err:
            raise err

        if response.status >= 400:
            raise InstagramPublicAPIInvalidResponseError

        return data

    def search_hashtag(self, name):
        name = name.lstrip("#")
        cursor = None

        while True:
            url = forge_hashtag_search_url(name, cursor=cursor)
            print(url, cursor)

            data = self.request_json(url)

            data = getpath(data, ["data", "hashtag", "edge_hashtag_to_media"])
            edges = data.get("edges")

            for edge in edges:
                yield edge["node"]["shortcode"]

            print("Found %i posts" % len(edges))

            has_next_page = getpath(data, ["page_info", "has_next_page"])

            if not has_next_page:
                break

            cursor = getpath(data, ["page_info", "end_cursor"])
