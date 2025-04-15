from typing import Tuple

from ural import URLFormatter, urlpathsplit

from minet.tiktok.constants import (
    TIKTOK_HTTP_API_BASE_URL,
    TIKTOK_COMMERCIAL_CONTENTS_FIELDS,
)


def parse_post_url(url: str) -> Tuple[str, str]:
    path = urlpathsplit(url)

    did = path[1]
    rkey = path[3]

    return did, rkey


class TikTokHTTPAPIUrlFormatter(URLFormatter):
    BASE_URL = TIKTOK_HTTP_API_BASE_URL

    def create_session(self) -> str:
        return self.format(
            path="oauth/token/",
        )

    def search_commercial_contents(self) -> str:
        return self.format(
            path="research/adlib/commercial_content/query/",
            args={"fields": TIKTOK_COMMERCIAL_CONTENTS_FIELDS},
        )
