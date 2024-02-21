from typing import Any

from bs4 import SoupStrainer, BeautifulSoup

from .types import NamedScraper


class TitleScraper(NamedScraper):
    name = "title"
    fieldnames = ["title"]
    plural = False
    output_type = "scalar"
    strainer = SoupStrainer(name="title")

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        title_elem = soup.find(name="title")

        if title_elem is None:
            return None

        return title_elem.get_text().strip()
