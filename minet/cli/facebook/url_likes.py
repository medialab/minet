# =============================================================================
# Minet Facebook Url Likes CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving approximate
# likes count by scraping Facebook's like button plugin.
#
from typing import Optional

import re
from urllib.parse import quote
from ural import is_url

from minet.rate_limiting import rate_limited
from minet.web import request
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.exceptions import FatalError

REPORT_HEADERS = ["approx_likes", "approx_likes_int"]
NUMBER_RE = re.compile(rb">(\d+\.?\d*[KM]?)<", re.I)


def forge_url(url):
    return (
        "https://www.facebook.com/plugins/share_button.php?href=%s&layout=button_count"
        % quote(url)
    )


@rate_limited(5)
def make_request(url: str) -> Optional[bytes]:
    response = request(forge_url(url), headers={"Accept-Language": "en"})

    if response.status == 404:
        return None

    return response.body


def scrape(data: bytes):
    match = NUMBER_RE.search(data)

    if match is None:
        return ["", ""]

    approx_likes = match.group(1).decode()
    approx_likes_int = approx_likes

    if "K" in approx_likes:
        approx_likes_int = str(int(float(approx_likes[:-1]) * 10**3))

    elif "M" in approx_likes:
        approx_likes_int = str(int(float(approx_likes[:-1]) * 10**6))

    return [approx_likes, approx_likes_int]


@with_enricher_and_loading_bar(
    headers=REPORT_HEADERS, title="Scraping likes", unit="urls"
)
def action(cli_args, enricher, loading_bar):
    for row, url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            url = url.strip()

            if not url or not is_url(url, require_protocol=False):
                enricher.writerow(row)
                continue

            try:
                html = make_request(url)
            except Exception:
                raise FatalError(
                    "An error occurred while fetching like button for this url: %s"
                    % url
                )

            if html is None:
                raise FatalError("Could not find data for this url: %s" % url)

            scraped = scrape(html)

            if scraped is None:
                raise FatalError(
                    "Could not extract Facebook likes from this url's like button: %s"
                    % url
                )

            enricher.writerow(row, scraped)
