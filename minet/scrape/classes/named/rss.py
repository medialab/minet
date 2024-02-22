from urllib.parse import urljoin
from ural import could_be_rss
from bs4 import SoupStrainer, BeautifulSoup

from .types import NamedScraper


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
