from typing import Optional, List, Any
from minet.types import AnyScrapableTarget

from bs4 import SoupStrainer
from casanova import CSVSerializer

from minet.scrape.analysis import ScraperAnalysisOutputType
from minet.scrape.utils import ensure_soup
from minet.scrape.mixin import ScraperMixin


class NamedScraper(ScraperMixin):
    fieldnames: List[str]
    plural: bool
    output_type: ScraperAnalysisOutputType
    strainer: Optional[SoupStrainer]
    serializer = CSVSerializer()

    def __call__(self, html: AnyScrapableTarget, context=None) -> Any:
        raise NotImplementedError


class TitleScraper(NamedScraper):
    fieldnames = ["title"]
    plural = False
    output_type = "scalar"
    strainer = SoupStrainer(name="title")

    def __call__(self, html: AnyScrapableTarget, context=None) -> Any:
        soup = ensure_soup(html, strainer=self.strainer)

        title_elem = soup.find(name="title")

        if title_elem is None:
            return None

        return title_elem.get_text().strip()


TYPICAL_SCRAPERS = {"title": TitleScraper}
