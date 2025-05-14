from typing import Iterator, Optional, List, Dict
from time import time

from minet.web import (
    request,
    create_request_retryer,
    create_pool_manager,
    retrying_method,
)

from minet.tiktok.urls import (
    TiktokHTTPAPIUrlFormatter,
)
from minet.tiktok.types import TiktokCommercialContent
from minet.tiktok.constants import TIKTOK_COMMERCIAL_CONTENTS_MAX_COUNT
from minet.tiktok.exceptions import TiktokAuthenticationError, TiktokHTTPAPIError


class TiktokHTTPClient:
    def __init__(self, identifier: str, password: str):
        self.urls = TiktokHTTPAPIUrlFormatter()
        self.pool_manager = create_pool_manager()
        self.retryer = create_request_retryer()

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

        response = request(
            self.urls.create_session(),
            pool_manager=self.pool_manager,
            method="POST",
            urlencoded_body=data,
            headers=headers,
        )

        if response.status != 200:
            raise TiktokAuthenticationError

        data = response.json()

        self.expired_at = time() + data["expires_in"]
        self.access_token = data["access_token"]

    def is_token_expired(self):
        return self.expired_at - time() < 10

    @retrying_method()
    def request(self, url: str, params: Dict, headers: Dict):
        if self.is_token_expired():
            self.create_session()

        response = request(
            url,
            pool_manager=self.pool_manager,
            method="POST",
            json_body=params,
            known_encoding="utf-8",
            headers=headers,
        )

        return response

    def search_commercial_contents(
        self,
        country: str,
        min_date: str,
        max_date: str,
        usernames: Optional[List[str]] = [],
    ) -> Iterator[Dict]:
        headers = {
            "authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json",
        }

        filters = {
            "content_published_date_range": {"min": min_date, "max": max_date},
            "creator_country_code": country,
        }

        params = {
            "filters": filters,
            "max_count": TIKTOK_COMMERCIAL_CONTENTS_MAX_COUNT,
        }

        if usernames:
            filters["creator_usernames"] = usernames

        url = self.urls.search_commercial_contents()

        while True:
            response = self.request(url, params, headers)

            data = response.json()

            if data["error"]["code"] != "ok":
                raise TiktokHTTPAPIError(data["error"])

            for content in data["data"]["commercial_contents"]:
                yield TiktokCommercialContent.from_payload(content, collected_via="api")

            has_more = data["data"]["has_more"]

            if has_more:
                params["search_id"] = data["data"]["search_id"]
            else:
                break
