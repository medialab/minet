from typing import Any

from bs4 import SoupStrainer, BeautifulSoup

from .types import NamedScraper


class MetasScraper(NamedScraper):
    name = "metas"
    fieldnames = [
        "name",
        "property",
        "http-equiv",
        "itemprop",
        "content",
        "charset",
    ]
    plural = True
    output_type = "collection"
    strainer = SoupStrainer(name="meta")

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        meta_elems = soup.find_all(name="meta")

        metas = []

        for meta_elem in meta_elems:
            metas.append({name: meta_elem.get(name) for name in self.fieldnames})

        return metas
