from typing import Optional, List, Any
from minet.types import AnyScrapableTarget

from bs4 import SoupStrainer, BeautifulSoup
from casanova import CSVSerializer
from ural import should_follow_href

from minet.scrape.analysis import ScraperAnalysisOutputType
from minet.scrape.utils import ensure_soup
from minet.scrape.mixin import ScraperMixin


class NamedScraper(ScraperMixin):
    name: str
    fieldnames: List[str]
    plural: bool
    output_type: ScraperAnalysisOutputType
    strainer: Optional[SoupStrainer]
    serializer = CSVSerializer()

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        raise NotImplementedError

    def __call__(self, html: AnyScrapableTarget, context=None) -> Any:
        soup = ensure_soup(html, strainer=self.strainer)
        return self.scrape(soup, context=None)


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

        url = url.strip()

        if not url:
            return None

        return url


class UrlsScraper(NamedScraper):
    name = "urls"
    fieldnames = ["url"]
    plural = True
    output_type = "list"
    strainer = SoupStrainer(name="a")

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:
        a_elems = soup.select("a[href]")

        urls = []

        for a in a_elems:
            url = a.get("href")

            if url is None:
                continue

            url = url.strip()

            if not url:
                continue

            if not should_follow_href(url):
                continue

            urls.append(url)

        return urls


TYPICAL_SCRAPERS = {s.name: s for s in [TitleScraper, CanonicalScraper, UrlsScraper]}
