from typing import List, Iterator
from minet.types import Literal

from dataclasses import dataclass
from ural.lru import LRUTrie
from ural import should_follow_href
from casanova import TabularRecord

from minet.crawl.spiders import Spider, SpiderResult
from minet.crawl.types import CrawlJob
from minet.web import Response
from minet.scrape.typical import UrlsScraper

WebentityStatus = Literal["IN", "OUT", "UNDECIDED", "DISCOVERED"]


@dataclass
class WebentityRecord:
    id: str
    status: WebentityStatus


@dataclass
class WebentityLink(TabularRecord):
    source_webentity: str
    target_webentity: str
    source_url: str
    target_url: str


class HypheSpider(Spider):
    def __init__(self):
        self.trie: LRUTrie[WebentityRecord] = LRUTrie()
        self.urls_scraper = UrlsScraper()

    def set(self, prefix, webentity, status: WebentityStatus = "IN") -> None:
        self.trie.set(prefix, WebentityRecord(id=webentity, status=status))

    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        if response.status != 200:
            return

        if not response.could_be_html:
            return

        webentity = self.trie.match(response.end_url)

        if webentity is None or webentity.status != "IN":
            return

        urls = self.urls_scraper(response.text())

        urls_to_follow = []
        links: List[WebentityLink] = []

        for url in urls:
            url = response.resolve(url)

            if not should_follow_href(url):
                continue

            match = self.trie.match(url)

            if match is None:
                continue

            if match.status != "IN":
                continue

            links.append(
                WebentityLink(
                    source_webentity=webentity.id,
                    target_webentity=match.id,
                    source_url=response.end_url,
                    target_url=url,
                )
            )

            if match.id != webentity.id:
                continue

            urls_to_follow.append(url)

        return links, urls_to_follow

    def tabulate(self, data: List[WebentityLink]) -> Iterator[WebentityLink]:
        yield from data
