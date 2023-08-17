from typing import Iterable, List, Set, Iterator, Any, Optional
from minet.types import Literal

from dataclasses import dataclass
from ural.lru import CanonicalizedLRUTrie
from ural import links_from_html, could_be_html, infer_redirection, canonicalize_url
from casanova import TabularRecord
from functools import lru_cache

from minet.crawl.spiders import Spider, SpiderResult
from minet.crawl.types import CrawlJob, SuccessfulCrawlResult
from minet.web import Response, resolve

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


def extract_links(url: str, body: bytes, encoding: str) -> List[str]:
    return list(
        links_from_html(
            url,
            body,
            encoding=encoding,
            canonicalize=True,
            unique=True,
            strip_fragment=True,
        )
    )


@lru_cache(2048)
def resolve_shortened_link(url: str) -> str:
    try:
        stack = resolve(url)
        last_url = stack[-1].url
        return last_url
    except Exception:
        return url


class HypheSpider(Spider):
    def __init__(self, ignore_internal_links: bool = False):
        self.trie: CanonicalizedLRUTrie[WebentityRecord] = CanonicalizedLRUTrie(
            suffix_aware=True, strip_fragment=True
        )
        self.start_pages: Set[str] = set()
        self.ignore_internal_links = ignore_internal_links

    def start(self) -> Iterable[str]:
        yield from self.start_pages

    def add_start_page(self, url: str) -> None:
        if self.is_attached:
            raise RuntimeError("cannot add start page if spider is already attached")

        self.start_pages.add(canonicalize_url(url, strip_fragment=True))

    def set(self, prefix, webentity, status: WebentityStatus = "IN") -> None:
        if status not in VALID_WEBENTITY_STATUSES:
            raise TypeError("invalid webentity status: {!r}".format(status))

        self.trie.set(prefix, WebentityRecord(id=webentity, status=status))

    def process(self, job: CrawlJob, response: Response) -> SpiderResult:
        if response.status != 200:
            return

        if not response.is_html:
            return

        webentity = self.trie.match(response.end_url)

        if webentity is None or webentity.status != "IN":
            return

        urls = self.submit(
            extract_links, response.end_url, response.body, response.likely_encoding
        )

        urls_to_follow = []
        links: List[WebentityLink] = []

        for url in urls:
            url = infer_redirection(url)

            if not could_be_html(url):
                continue

            # if is_shortened_url(url):
            #     url = resolve_shortened_link(url)

            match = self.trie.match(url)

            if match is None:
                continue

            if match.status != "IN":
                continue

            if not self.ignore_internal_links or webentity.id != match.id:
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
