from typing import Optional, List, Any, Dict, Type, cast

from bs4 import SoupStrainer, BeautifulSoup, MarkupResemblesLocatorWarning
from datetime import datetime
from html import unescape
import locale
from urllib.parse import urljoin
from ural import should_follow_href, could_be_rss
import warnings

from minet.scrape.analysis import ScraperAnalysisOutputType
from minet.scrape.utils import ensure_soup
from minet.scrape.types import AnyScrapableTarget
from minet.scrape.classes.base import ScraperBase

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

DAYS_OF_WEEK_FR = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche"
]
DAYS_OF_WEEK_EN = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]


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

        url = cast(str, url).strip()

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


class RssScraper(NamedScraper):
    name = "rss"
    fieldnames = ["rss_url"]
    plural = True
    output_type = "list"
    strainer = SoupStrainer(name=["a", "link"])

    def scrape(self, soup: BeautifulSoup, context=None):
        rss_urls = []
        base_url = context.get("url") if context is not None else ""

        for link in soup.find_all():
            if link.name == "link":
                type_attr = link.attrs.get("type", None)
                if (
                    type_attr == "application/rss+xml"
                    or type_attr == "application/atom+xml"
                ):
                    href = link.attrs.get("href", None)
                    if href:
                        rss_urls.append(urljoin(base_url, href))
            else:
                href = link.attrs.get("href", None)
                url = urljoin(base_url, href)
                if could_be_rss(url):
                    rss_urls.append(url)

        return rss_urls

def extract_date(doc_header):
 date = ""
 date_index = 0
 found_date = False
 doc_header_list = doc_header.split(" ")

 for enum, word in enumerate(doc_header_list):

    if word.lower() in DAYS_OF_WEEK_FR:
        found_date = True
        date_index = enum
        loc = locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
    elif word.strip(",").lower() in DAYS_OF_WEEK_EN:
        found_date = True
        date_index = enum
        loc = locale.setlocale(locale.LC_ALL, 'en_US.utf8')

    if found_date:

        if enum in range(date_index, date_index + 3):
            date += word + " "

        elif enum == date_index + 3:
            date += word

            try:
                if loc[:2] == "fr":
                    formatted_date = datetime.strptime(date, "%A %d %B %Y")
                else:
                    formatted_date = datetime.strptime(date, "%A, %B %d, %Y")

                return formatted_date.date().isoformat()

            except ValueError:
                return extract_date(" ".join(doc_header_list[enum:]))

def select_and_strip(elem, selector):
    selected_elem = elem.select_one(selector)

    if selected_elem is None:
        return ""

    return selected_elem.get_text().strip()

class EuropresseScraper(NamedScraper):
    name = "europresse"
    fieldnames = ["id", "title", "content", "url", "date", "media"]
    plural = True
    output_type = "collection"
    strainer = SoupStrainer(name = "article")

    def scrape(self, soup: BeautifulSoup, context=None) -> Any:

        articles = []
        selectors = {
            "title": ".titreArticle",
            "id": ".publiC-lblNodoc",
            "date": ".DocHeader",
            "media": ".DocPublicationName"
        }


        for elem in soup.select("article"):

            row = {}

            content = elem.select_one(".docOcurrContainer")
            if content is None:
                content = ""
            else:
                urls = content.select("a")
                for u in urls:
                    if "Cet article est paru dans" in u.get_text():
                        row["url"] = u.get("href")
                        break
                content = content.get_text()


            for field, selector in selectors.items():
                row[field] = select_and_strip(elem, selector)

            row["content"] = BeautifulSoup(unescape(content), "html.parser").get_text().strip()
            row["date"] = extract_date(row["date"])
            row["media"] = row["media"]\
            .split(",")[0]\
            .split("\n")[0]\
            .split("                ")[0]\
            .strip()

            articles.append(row)

        return articles


NAMED_SCRAPERS: Dict[str, Type[NamedScraper]] = {
    s.name: s
    for s in [
        TitleScraper,
        CanonicalScraper,
        UrlsScraper,
        ImagesScraper,
        MetasScraper,
        RssScraper,
        EuropresseScraper
    ]
}
