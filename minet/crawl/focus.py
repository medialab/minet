import re
import ural
from typing import List
from collections.abc import Iterable
from urllib.parse import urljoin
from dataclasses import dataclass

from minet.web import looks_like_html
from minet.crawl.types import CrawlJob
from minet.extraction import extract
from minet.web import Response
from minet.crawl.spiders import Spider


@dataclass
class FocusCrawlResult:
    relevant: bool
    matches: int
    ignored_url: List[str]

    """
    def __init__(self, relevant, matches, ignored_url) -> None:
        self.relevant = relevant
        self.matches = matches
        self.ignored_url = ignored_url
    """


class FocusSpider(Spider):
    def clean_url(self, origin, url):
        url = urljoin(origin, url)
        return ural.normalize_url(url)

    def __init__(
        self,
        start_urls,
        max_depth=3,
        regex_content=None,
        regex_url=None,
        irrelevant_continue=False,
        extract=False,
        only_target_html_page=True,
    ):

        if not isinstance(max_depth, int) or max_depth < 0:
            raise TypeError("Max depth needs to be a positive integer.")

        if not regex_content and not regex_url:
            raise TypeError("Neither url nor content filter provided.")

        self.depth = max_depth
        self.urls = start_urls
        self.regex_content = re.compile(regex_content, re.I) if regex_content else None
        self.regex_url = re.compile(regex_url, re.I) if regex_url else None
        self.extraction = extract
        self.irrelevant_continue = irrelevant_continue
        self.target_html = only_target_html_page

    def __call__(self, job: CrawlJob, response: Response):

        # Return variables
        relevant_content = False
        next_urls = set()
        ignored_urls = set()

        end_url = response.end_url

        html = response.body
        if (self.target_html and not looks_like_html(html)):
            return FocusCrawlResult(False, 0, None), []
        if not response.is_text or not html:
            return FocusCrawlResult(False, 0, None), []

        html = response.text()
        soup = response.soup(ignore_xhtml_warning=True)

        if self.extraction:
            extraction = extract(html)
            if extraction:
                content = extraction.blurb()
        else:
            content = soup.get_text()

        a_tags = soup.find_all("a")
        links = set(
            self.clean_url(end_url, a.get("href"))
            for a in a_tags
            if a.get("href") and ural.should_follow_href(a.get("href"))
        )

        if self.regex_content:
            match = self.regex_content.findall(content)
            relevant_content = bool(match)
            relevant_size = len(match) if match else 0
        else:
            relevant_content = True
            relevant_size = None

        if not self.regex_url:
            next_urls = links
        else:
            for a in links:
                if self.regex_url.search(a):
                    if self.target_html:
                        if ural.could_be_html(a):
                            next_urls.add(a)
                        else:
                            ignored_urls.add(a)
                    else:
                        next_urls.add(a)
                else:
                    ignored_urls.add(a)

        if (
            not relevant_content and not self.irrelevant_continue
        ) or job.depth + 1 > self.depth:
            next_urls = set()

        rep_obj = FocusCrawlResult(relevant_content, relevant_size, ignored_urls)

        return rep_obj, next_urls

    def start(self):
        yield from self.urls
