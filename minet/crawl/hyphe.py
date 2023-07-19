from typing import Iterable, List, Set, Iterator, Any, Optional
from minet.types import Literal

from dataclasses import dataclass
from ural.lru import LRUTrie
from ural import should_follow_href
from casanova import TabularRecord

from minet.crawl.spiders import Spider, SpiderResult
from minet.crawl.types import CrawlJob, SuccessfulCrawlResult
from minet.web import Response
from minet.scrape.typical import UrlsScraper

VALID_WEBENTITY_STATUSES = ["IN", "OUT", "UNDECIDED", "DISCOVERED"]

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


@dataclass
class HypheSpiderAddendum:
    webentity_id: str
    links: List[WebentityLink]


class HypheSpider(Spider):
    def __init__(self):
        self.trie: LRUTrie[WebentityRecord] = LRUTrie(suffix_aware=True)
        self.urls_scraper = UrlsScraper()
        self.start_pages: Set[str] = set()

    def start(self) -> Iterable[str]:
        yield from self.start_pages

    def add_start_page(self, url: str) -> None:
        if self.is_attached:
            raise RuntimeError("cannot add start page if spider is already attached")

        self.start_pages.add(url)

    def set(self, prefix, webentity, status: WebentityStatus = "IN") -> None:
        if status not in VALID_WEBENTITY_STATUSES:
            raise TypeError("invalid webentity status: {!r}".format(status))

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
            url = response.urljoin(url)

            if not should_follow_href(url):
                continue

            # TODO: drop when issue is pinpointed
            try:
                match = self.trie.match(url)
            except Exception:
                raise TypeError(url)

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

        return (
            HypheSpiderAddendum(webentity_id=webentity.id, links=links),
            urls_to_follow,
        )

    def tabulate(
        self, result: SuccessfulCrawlResult[Any, Optional[HypheSpiderAddendum]]
    ) -> Iterator[WebentityLink]:
        if not result.data:
            return

        yield from result.data.links
