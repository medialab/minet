# =============================================================================
# Minet Tiktok API Scraper
# =============================================================================
#
# Tiktok public API "scraper".
#
from ebbe import getpath
from urllib.parse import quote
from typing import Optional, Dict
from datetime import datetime

from minet.utils import sleep_with_entropy
from minet.cookies import coerce_cookie_for_url_from_browser
from minet.web import (
    create_pool_manager,
    create_request_retryer,
    request,
    retrying_method,
)
from minet.tiktok.constants import (
    TIKTOK_DEFAULT_THROTTLE,
    TIKTOK_PUBLIC_API_DEFAULT_TIMEOUT,
    TIKTOK_URL,
    TIKTOK_MIN_TIME_RETRYER,
    TIKTOK_MAX_RANDOM_ADDENDUM,
    TIKTOK_COMMERCIAL_CONTENTS_MAX_COUNT,
)
from minet.tiktok.exceptions import (
    TiktokInvalidCookieError,
    TiktokPublicAPIInvalidResponseError,
)
from minet.tiktok.types import TiktokVideo, TiktokCommercialContent


def forge_video_search_url(query, offset, search_id=None):
    url = (
        "https://t.tiktok.com/api/search/general/full/?aid=1988&keyword=%s&offset=%s"
        % (quote(query), offset)
    )

    if search_id is not None:
        url += "&search_id=%s" % search_id

    return url


def forge_commercials_raw_data(
    username: str = "",
    search_id: str = "",
):
    return {
        "order": "posted_date,desc",
        "cursor": 0,
        "size": TIKTOK_COMMERCIAL_CONTENTS_MAX_COUNT,
        "search_id": search_id,
        "query": username,
    }


class TiktokAPIScraper(object):
    def __init__(self, cookie=None):
        self.pool_manager = create_pool_manager(
            timeout=TIKTOK_PUBLIC_API_DEFAULT_TIMEOUT
        )

        if cookie:
            cookie = coerce_cookie_for_url_from_browser(cookie, TIKTOK_URL)

            if not cookie:
                raise TiktokInvalidCookieError

        self.cookie = cookie

        self.retryer = create_request_retryer(
            min=TIKTOK_MIN_TIME_RETRYER,
        )

    @retrying_method()
    def request_json(self, url: str, body: Optional[Dict] = None, method: str = "GET"):
        headers = {"Cookie": self.cookie} if self.cookie else {}

        response = request(
            url,
            pool_manager=self.pool_manager,
            spoof_ua=True,
            headers=headers,
            json_body=body,
            method=method,
        )

        if response.status >= 400:
            raise TiktokPublicAPIInvalidResponseError(
                url, response.status, response.text()
            )

        sleep_with_entropy(TIKTOK_DEFAULT_THROTTLE, TIKTOK_MAX_RANDOM_ADDENDUM)

        return response.json()

    def search_commercial_contents(
        self,
        country: str,
        min_date: str,
        max_date: str,
        username: str = "",
    ):
        search_id = ""
        min_timestamp = int(datetime.strptime(min_date, "%Y%m%d").timestamp())
        max_timestamp = int(datetime.strptime(max_date, "%Y%m%d").timestamp())
        url = (
            "https://library.tiktok.com/api/v1/other-commercial-contents/search?region=%s&start_time=%i&end_time=%i"
            % (country, min_timestamp, max_timestamp)
        )

        while True:
            body = forge_commercials_raw_data(username, search_id)
            data = self.request_json(url, body, "POST")
            item_list = data.get("data")

            if not item_list:
                break

            for item in item_list:
                commercial = TiktokCommercialContent.from_payload(
                    item, collected_via="scrape"
                )
                yield commercial

            has_next_page = getpath(data, ["has_more"])
            search_id = getpath(data, ["search_id"])

            if not has_next_page or search_id is None:
                break

    def search_videos(self, query):
        cursor = None
        search_id = None

        # NOTE: search is not very consistent and return the same often more than once
        # Since there is a hard limit of max results around ~500, we can tolerate
        # saving all ids in memory
        already_seen = set()

        while True:
            url = forge_video_search_url(query, cursor, search_id)

            data = self.request_json(url)
            item_list = data.get("data")

            if not item_list:
                break

            for item in item_list:
                if item["type"] != 1:
                    continue

                item = item["item"]
                video = TiktokVideo.from_payload(item)

                # NOTE: avoiding pagination hiccups
                if video.id in already_seen:
                    continue

                already_seen.add(video.id)
                yield video

            has_next_page = getpath(data, ["has_more"])
            search_id = getpath(data, ["extra", "logid"])

            if has_next_page != 1 or search_id is None:
                break

            cursor = getpath(data, ["cursor"])
