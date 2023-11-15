from typing import List, Optional, Any
from minet.types import Literal

import re
from ural import could_be_html, normalize_url, should_follow_href
from urllib.parse import urljoin
from dataclasses import dataclass
from casanova import TabularRecord

from minet.web import looks_like_html
from minet.crawl.types import CrawlJob, SuccessfulCrawlResult
from minet.extraction import extract
from minet.web import Response
from minet.crawl.spiders import Spider


FocusCrawlContentInvalidity = Literal["irrelevant", "not-html", "binary", "empty"]
FocusCrawlLinkInvalidity = Literal["irrelevant", "not-html"]


@dataclass
class FocusCrawLinkReport(TabularRecord):
    source: str
    target: str
    source_is_relevant: bool
    source_content_invalidity: Optional[FocusCrawlContentInvalidity]
    target_is_relevant: bool
    target_link_invalidity: Optional[FocusCrawlLinkInvalidity]


@dataclass
class FocusCrawLink:
    url: str
    invalidity: Optional[FocusCrawlLinkInvalidity] = None

    @property
    def relevant(self) -> bool:
        return self.invalidity is None


@dataclass
class FocusCrawlInfo:
    CRAWL_RESULT_ADDENDUM_FIELDNAMES = ["relevant", "invalidity", "matches"]

    invalidity: Optional[FocusCrawlContentInvalidity] = None
    matches: Optional[int] = None
    links: Optional[List[FocusCrawLink]] = None

    @property
    def relevant(self) -> bool:
        return self.invalidity is None

    def as_crawl_result_csv_addendum(self):
        return ["yes" if self.relevant else "no", self.invalidity, self.matches]


class FocusSpider(Spider):
    def clean_url(self, origin, url):
        url = urljoin(origin, url)
        return normalize_url(url)

    def url_relevance(self, url):
        if self.regex_url:
            m = bool(self.regex_url.search(url))

            if self.invert_url_match:
                m = not m

            return m

        return True

    def content_relevance(self, content):
        if self.regex_content:
            matches = self.regex_content.findall(content)
            if self.invert_content_match:
                return not bool(matches), None
            else:
                return bool(matches), len(matches) if matches else None
        else:
            return True, None

    def __init__(
        self,
        start_urls=None,
        regex_content=None,
        invert_content_match: bool = False,
        regex_url=None,
        invert_url_match: bool = False,
        irrelevant_continue: bool = False,
        extract: bool = False,
        only_html: bool = True,
        extraction_fields=None,
    ):
        if not regex_content and not regex_url:
            raise TypeError("Neither url nor content filter provided.")

        if extraction_fields and not extract:
            raise TypeError(
                "Custom extraction fields can't be used without the extract option."
            )

        self.urls = start_urls
        self.regex_content = re.compile(regex_content, re.I) if regex_content else None
        self.invert_content_match = invert_content_match
        self.regex_url = re.compile(regex_url, re.I) if regex_url else None
        self.invert_url_match = invert_url_match
        self.extraction = extract
        self.extraction_fields = extraction_fields
        self.irrelevant_continue = irrelevant_continue
        self.target_html = only_html

    def process(self, job: CrawlJob, response: Response):
        has_relevant_content = False
        html = response.body

        if self.target_html and not looks_like_html(html):
            return FocusCrawlInfo(invalidity="not-html"), None
        if not response.is_text:
            return FocusCrawlInfo(invalidity="binary"), None
        if not html:
            return FocusCrawlInfo(invalidity="empty")

        html = response.text()
        soup = response.soup(ignore_xhtml_warning=True)

        content = ""

        if self.extraction:
            extraction = extract(html)
            if extraction:
                content = extraction.blurb(self.extraction_fields)
        else:
            content = soup.get_text()

        a_tags = soup.select("a[href]")
        unique_urls = set()

        for a in a_tags:
            url = a.get("href")

            assert isinstance(url, str)

            if not should_follow_href(url):
                continue

            unique_urls.add(response.urljoin(url))

        has_relevant_content, relevant_size = self.content_relevance(content)

        links = [FocusCrawLink(url=url) for url in unique_urls]
        next_urls = []

        for link in links:
            url = link.url

            if self.target_html and not could_be_html(url):
                link.invalidity = "not-html"
                continue

            if not self.url_relevance(url):
                link.invalidity = "irrelevant"
                continue

            next_urls.append(url)

        if not has_relevant_content and not self.irrelevant_continue:
            next_urls = set()

        info = FocusCrawlInfo(
            invalidity="irrelevant" if not has_relevant_content else None,
            matches=relevant_size,
            links=links,
        )

        return info, next_urls

    def start(self):
        if not self.urls:
            return

        yield from self.urls

    def tabulate(self, result: SuccessfulCrawlResult[Any, FocusCrawlInfo]):
        info = result.data
        source_url = result.response.end_url

        if not info.links:
            return

        for link in info.links:
            yield FocusCrawLinkReport(
                source=source_url,
                target=link.url,
                source_is_relevant=info.relevant,
                source_content_invalidity=info.invalidity,
                target_is_relevant=link.relevant,
                target_link_invalidity=link.invalidity,
            )
