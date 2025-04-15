from typing import Iterator, Optional, List, Dict
import requests

from minet.web import (
    create_request_retryer,
    create_pool_manager,
    retrying_method,
)

from minet.tiktok.urls import (
    TikTokHTTPAPIUrlFormatter,
)
from minet.tiktok.constants import TIKTOK_COMMERCIAL_CONTENTS_MAX_COUNT
from minet.bluesky.exceptions import BlueskyAuthenticationError


class TikTokHTTPClient:
    def __init__(self, identifier: str, password: str):
        self.urls = TikTokHTTPAPIUrlFormatter()
        self.pool_manager = create_pool_manager()
        self.retryer = create_request_retryer()
        self.rate_limit_reset: Optional[int] = None

        # First auth
        self.create_session(identifier, password)

    @retrying_method()
    def create_session(self, key: str, secret: str):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_key": key,
            "client_secret": secret,
            "grant_type": "client_credentials",
        }

        response = requests.post(self.urls.create_session(), headers=headers, data=data)

        if response.status_code != 200:
            raise BlueskyAuthenticationError

        data = response.json()

        self.access_token = data["access_token"]
        self.expired_in = data["expires_in"]

    def search_commercial_contents(
        self,
        country_code: str,
        start_date: str,
        end_date: str,
        usernames: Optional[List[str]] = [],
        max_results: Optional[int] = None,
    ) -> Iterator[Dict]:
        headers = {
            "authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json",
        }

        filters = {
            "content_published_date_range": {"min": start_date, "max": end_date},
            "creator_country_code": country_code,
        }

        params = {"filters": filters, "max_count": TIKTOK_COMMERCIAL_CONTENTS_MAX_COUNT}

        if usernames:
            filters["creator_usernames"] = usernames

        counter = 0

        while True:
            url = self.urls.search_commercial_contents()

            response = requests.post(url, headers=headers, json=params)
            data = response.json()

            for video in data["data"]["commercial_contents"]:
                if counter >= max_results:
                    return

                yield video
                counter += 1

            has_more = data["data"]["has_more"]

            if has_more:
                params["search_id"] = data["data"]["search_id"]
            else:
                break
