import re
import bs4
import ural
from trafilatura import bare_extraction
from ural import urls_from_text, urls_from_html
from urllib.parse import urljoin
from urllib.parse import unquote

from typing import Iterable, Optional
from minet.crawl.spiders import SpiderResult
from minet.crawl.types import CrawlJob, UrlOrCrawlTarget
from minet.extraction import extract
from minet.web import Response
from minet.crawl.spiders import Spider

MODE_REGEX = "regex"
MODE_KEYWORD = "keyword"

class FocusSpider(Spider):

    class FocusResponse():
        def __init__(self, interesting, ignored_url) -> None:
            self.interesting = interesting
            self.ignored_url = ignored_url

    # None
    def __init__(
        self,
        start_urls,
        max_depth,
        regex_content = None,
        regex_url = None,
        keywords = None,
        stop_when_not_interesting = True,
        perform_on_html=False,
        only_target_html_page=True):

        super().__init__()

        self.START_URLS = start_urls
        self.START_URL = None

        self.regex_content = re.compile(regex_content, re.I) if regex_content else None
        self.regex_url = re.compile(regex_url, re.I) if regex_url else None
        self.keywords = keywords
        self.extraction = not perform_on_html
        self.depth = max_depth
        self.interesting_stop = stop_when_not_interesting
        self.target_html = only_target_html_page


    # Tuple[Any, Iterable[str | CrawlTarget] | None] | None
    # Any : ce qu'on veut renvoyer dans l'itération du résultat du crawler
    def __call__(self, job: CrawlJob, response: Response):


        # Return variables
        interesting_content = False
        next_urls = []
        ignored_urls = []

        if job.depth > self.depth:
            return (None, None)

        html = response.text()
        if not response.is_text and not html:
            return (None, None)

        content = html


        if self.extraction:
            dico_content = extract(content)
            items = [
                dico_content.title,
                dico_content.description,
                dico_content.content,
                dico_content.comments,
                dico_content.author,
                dico_content.categories,
                dico_content.tags,
                dico_content.date,
                dico_content.sitename
            ]
            clist = [v for v in items if isinstance(v, str)]
            content = '\n'.join(clist)


        links = list(urls_from_text(html))
        links += [i for i in urls_from_html(html) if i not in links]

        if self.regex_content:
            match = self.regex_content.findall(content)
        elif self.keywords:
            match = all(k in content for k in self.keywords)


        interesting_content = bool(match)


        if not self.regex_url:
            for a in links:
                a = ural.normalize_url(unquote(urljoin(response.end_url, a)))
                next_urls.append(a)
        else:
            for a in links:
                ap = a
                a = ural.normalize_url(unquote(urljoin(response.end_url, a)))

                if self.regex_url.match(a):
                    if self.target_html:
                        if ural.could_be_html(ap): next_urls.append(a)
                        else: ignored_urls.append(a)
                    else: next_urls.append(a)
                else:
                    ignored_urls.append(a)


        if (not interesting_content and self.interesting_stop) or job.depth + 1 > self.depth:
            next_urls = []


        rep_obj = FocusSpider.FocusResponse(
            interesting_content,
            ignored_urls
        )


        return (rep_obj, next_urls)

    # Iterable[str | CrawlTarget] | None
    def start(self):
        return self.START_URLS
