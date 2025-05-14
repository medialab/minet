from ural import URLFormatter

from minet.tiktok.constants import (
    TIKTOK_HTTP_API_BASE_URL,
    TIKTOK_COMMERCIAL_CONTENTS_FIELDS,
)


class TiktokHTTPAPIUrlFormatter(URLFormatter):
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
