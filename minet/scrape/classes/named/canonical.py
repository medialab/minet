from typing import Any, cast

from bs4 import SoupStrainer, BeautifulSoup

from .types import NamedScraper


class CanonicalScraper(NamedScraper):
    name = "canonical"
    fieldnames = ["canonical_url"]
    plural = False
    output_type = "scalar"
    strainer = SoupStrainer(name="link", attrs={"rel": "canonical"})

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        link_elem = soup.select_one("link[rel=canonical][href]")

        if link_elem is None:
            return None

        url = link_elem.get("href")

        if url is None:
            return None

        url = cast(str, url).strip()

        if not url:
            return None

        return url
