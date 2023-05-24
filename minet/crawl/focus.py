import re
import bs4
import ural
from trafilatura import bare_extraction
from ural import urls_from_html
from urllib.parse import urljoin
from urllib.parse import unquote

from typing import Iterable, Optional
from minet.crawl.spiders import SpiderResult
from minet.crawl.types import CrawlJob, UrlOrCrawlTarget
from minet.web import Response
from minet.crawl.spiders import Spider

MODE_REGEX = "regex"
MODE_KEYWORD = "keyword"

class FocusSpider(Spider):

    class FocusResponse():
        def __init__(self, interesting, depth, content, ignored_url, next_urls) -> None:
            self.interesting = interesting
            self.depth = depth
            self.content = content
            self.ignored_url = ignored_url
            self.next_urls = next_urls

    # None
    def __init__(
        self,
        start_urls,
        max_depth,
        regex_content = None,
        regex_url = None,
        keywords = None,
        perform_on_html=False):

        super().__init__()
        if len(start_urls) == 1: self.START_URLS = start_urls
        else: self.START_URL = start_urls

        self.regex_content = re.compile(regex_content, re.I) if regex_content else None
        self.regex_url = re.compile(regex_url, re.I) if regex_url else None
        self.keywords = keywords
        self.extraction = not perform_on_html
        self.depth = max_depth


    # Tuple[Any, Iterable[str | CrawlTarget] | None] | None
    # Any : ce qu'on veut renvoyer dans l'itération du résultat du crawler
    def __call__(self, job: CrawlJob, response: Response):

        if job.depth > self.depth:
            return (None, None)

        html = response.text()
        if not html:
            return (None, None)

        content = html

        if self.extraction:
            dico_content = bare_extraction(content)
            clist = [v for (_, v) in dico_content.items() if v != None and v != []]
            content = '\n'.join(clist)
            #print(content)

        links = urls_from_html(html)

        if self.regex_content:
            match = self.regex_content.findall(content)
        elif self.keywords:
            match = all(k in content for k in self.keywords)
        if not match:
            response = FocusSpider.FocusResponse(
                False,
                job.depth,
                content,
                [ural.normalize_url(unquote(urljoin(response.end_url, a))) for a in links],
                []
            )
            return (response, None)


        next_urls = []
        ignored_urls = []

        if not self.regex_url:
            for a in links:
                next_urls.append(a)
        else:
            for a in links:
                a = urljoin(response.end_url, a)
                a = unquote(a)
                a = ural.normalize_url(a)

                if self.regex_url.match(a):
                    next_urls.append(a)
                else:
                    ignored_urls.append(a)



        response = FocusSpider.FocusResponse(
            True,
            job.depth,
            content,
            ignored_urls,
            next_urls if job.depth + 1 <= self.depth else []
        )


        return (response, next_urls if job.depth + 1 <= self.depth else None)

    # Iterable[str | CrawlTarget] | None
    def start(self):
        return self.START_URL if self.START_URL else self.START_URLS
