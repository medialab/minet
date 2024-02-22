from typing import Optional, List, Any

from bs4 import SoupStrainer, BeautifulSoup

from minet.scrape.analysis import ScraperAnalysisOutputType
from minet.scrape.utils import ensure_soup
from minet.scrape.types import AnyScrapableTarget
from minet.scrape.classes.base import ScraperBase


class NamedScraper(ScraperBase):
    name: str
    fieldnames: List[str]
    plural: bool
    tabular = True
    output_type: ScraperAnalysisOutputType
    strainer: Optional[SoupStrainer]

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        raise NotImplementedError

    def __call__(self, html: AnyScrapableTarget, context=None) -> Any:
        soup = ensure_soup(html, strainer=self.strainer)
        return self.scrape(soup, context=context)
