from typing import Any, cast

from urllib.parse import urljoin
from bs4 import SoupStrainer, BeautifulSoup
from ural import should_follow_href

from .types import NamedScraper


class UrlsScraper(NamedScraper):
    name = "urls"
    fieldnames = ["url"]
    plural = True
    output_type = "list"
    strainer = SoupStrainer(name="a")

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        a_elems = soup.select("a[href]")
        base_url = context.get("url") if context is not None else None

        urls = []

        for a in a_elems:
            url = a.get("href")

            if url is None:
                continue

            url = cast(str, url).strip()

            if not url:
                continue

            if not should_follow_href(url):
                continue

            if base_url:
                url = urljoin(base_url, url)

            urls.append(url)

        return urls
