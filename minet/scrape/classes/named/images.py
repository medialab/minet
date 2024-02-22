from typing import Any, cast

from bs4 import SoupStrainer, BeautifulSoup
from ural import should_follow_href
from urllib.parse import urljoin

from .types import NamedScraper


class ImagesScraper(NamedScraper):
    name = "images"
    fieldnames = ["src"]
    plural = True
    output_type = "list"
    strainer = SoupStrainer(name="img")

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        img_elems = soup.select("img[src]")
        base_url = context.get("url") if context is not None else None

        urls = []

        for img in img_elems:
            url = img.get("src")

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
