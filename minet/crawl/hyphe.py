from minet.types import Literal

from dataclasses import dataclass
from ural.lru import LRUTrie

from minet.crawl.spiders import Spider, SpiderResult
from minet.crawl.types import CrawlJob
from minet.web import Response
from minet.scrape.typical import UrlsScraper

WebentityStatus = Literal["IN", "OUT", "UNDECIDED", "DISCOVERED"]


@dataclass
class HypheJobData:
    webentity: str


class HypheSpider(Spider[HypheJobData, None]):
    def __init__(self):
        self.trie = LRUTrie()
        self.urls_scraper = UrlsScraper()

    def set(self, prefix, webentity, status: WebentityStatus = "IN") -> None:
        self.trie.set(prefix, webentity)

    def process(self, job: CrawlJob[HypheJobData], response: Response) -> SpiderResult:
        assert job.data is not None

        if response.status != 200:
            return None

        if not response.could_be_html:
            return None

        urls = self.urls_scraper(response.text())

        valid_urls = []

        for url in urls:
            match = self.trie.match(url)

            if match is None:
                continue

            if match != job.data.webentity:
                continue

            valid_urls.append(url)

        return None, valid_urls
