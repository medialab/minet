# =============================================================================
# Minet Tiktok API Scraper
# =============================================================================
#
# Tiktok public API "scraper".
#
from ebbe import getpath
from urllib.parse import quote

from minet.constants import COOKIE_BROWSERS
from minet.utils import sleep_with_entropy
from minet.web import (
    create_pool,
    create_request_retryer,
    request_json,
    grab_cookies,
    retrying_method,
)
from minet.tiktok.constants import (
    TIKTOK_DEFAULT_THROTTLE,
    TIKTOK_PUBLIC_API_DEFAULT_TIMEOUT,
    TIKTOK_URL,
    TIKTOK_MIN_TIME_RETRYER,
    TIKTOK_MAX_RANDOM_ADDENDUM,
)
from minet.tiktok.exceptions import (
    TiktokInvalidCookieError,
    TiktokPublicAPIInvalidResponseError,
)
from minet.tiktok.formatters import (
    format_video,
)


def forge_video_search_url(query, offset):

    url = (
        "https://www.tiktok.com/api/search/general/full/?aid=1988&keyword=%s&offset=%s"
        % (quote(query), offset)
    )

    return url


class TiktokAPIScraper(object):
    def __init__(self, cookie="firefox"):
        self.pool = create_pool(timeout=TIKTOK_PUBLIC_API_DEFAULT_TIMEOUT)

        if cookie in COOKIE_BROWSERS:
            get_cookie_for_url = grab_cookies(cookie)
            cookie = get_cookie_for_url(TIKTOK_URL)

        if not cookie:
            raise TiktokInvalidCookieError

        self.cookie = cookie
        self.retryer = create_request_retryer(
            min=TIKTOK_MIN_TIME_RETRYER,
        )

    @retrying_method()
    def request_json(self, url):
        headers = {"Cookie": self.cookie}
        err, response, data = request_json(
            url,
            pool=self.pool,
            spoof_ua=True,
            headers=headers,
        )

        if err:
            raise err

        if response.status >= 400:
            raise TiktokPublicAPIInvalidResponseError(url, response.status, data)

        sleep_with_entropy(TIKTOK_DEFAULT_THROTTLE, TIKTOK_MAX_RANDOM_ADDENDUM)

        return data

    def search_videos(self, query):
        cursor = None

        while True:
            url = forge_video_search_url(query, cursor)

            data = self.request_json(url)

            item_list = data.get("data")

            if not item_list:
                break

            for item in item_list:
                if item["type"] != 1:
                    continue
                item = item["item"]
                yield format_video(item)

            has_next_page = getpath(data, ["has_more"])

            if has_next_page != 1:
                break

            cursor = getpath(data, ["cursor"])
