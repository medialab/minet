import re
import ural
from bs4 import BeautifulSoup, SoupStrainer
from typing import Iterable, Optional
from ural import urls_from_text, urls_from_html
from urllib.parse import urljoin
from urllib.parse import unquote

from minet.cli.exceptions import FatalError
from minet.crawl.spiders import SpiderResult
from minet.web import looks_like_html
from minet.crawl.types import CrawlJob, UrlOrCrawlTarget
from minet.extraction import extract
from minet.web import Response
from minet.crawl.spiders import Spider

class FocusResponse:
    def __init__(self, interesting, ignored_url) -> None:
        self.interesting = interesting
        self.ignored_url = ignored_url

class FocusSpider(Spider):

    def clean_url(self, origin, url):
        url = urljoin(origin, url)
        return ural.normalize_url(ural)

    # None
    def __init__(
        self,
        start_urls,
        max_depth,
        regex_content = None,
        regex_url = None,
        uninteresting_continue = False,
        perform_on_html=False,
        only_target_html_page=True):

        self.urls = start_urls
        self.regex_content = re.compile(regex_content, re.I) if regex_content else None
        self.regex_url = re.compile(regex_url, re.I) if regex_url else None
        self.extraction = not perform_on_html
        self.depth = max_depth
        self.unteresting_continue = uninteresting_continue
        self.target_html = only_target_html_page



    # Tuple[Any, Iterable[str | CrawlTarget] | None] | None
    # Any : ce qu'on veut renvoyer dans l'itération du résultat du crawler
    def __call__(self, job: CrawlJob, response: Response):

        # Return variables
        interesting_content = False
        next_urls = set()
        ignored_urls = set()

        # Useful "constants"
        end_url = response.end_url

        if job.depth > self.depth:
            return None

        html = response.body
        if self.target_html and not looks_like_html(html):
            return (FocusResponse(False, None), [])
        if not response.is_text or not html:
            return (FocusResponse(False, None), [])

        html = response.text()
        content = html

        # NOTE
        # Warning : the use of trafiulatura
        # keeps printing the error :
        # "encoding error : input conversion failed due to input error ..."
        # and it has consequences on the terminal user interface of minet
        #
        # The problem seems to come from Trafilatura or BeautifulSoup

        if self.extraction:
            dico_content = extract(content)
            items = [
                dico_content.title,
                dico_content.description,
                dico_content.content,
                dico_content.comments,
                dico_content.author,
                ' '.join(dico_content.categories),
                ' '.join(dico_content.tags),
                dico_content.date,
                dico_content.sitename
            ]
            clist = [v for v in items if isinstance(v, str)]
            content = '\n'.join(clist)



        bs = BeautifulSoup(content, "html.parser", parse_only=SoupStrainer("a")).find_all("a")
        links = set(self.clean_url(end_url, a.get('href')) for a in bs if a.get('href'))

        if self.regex_content:
            match = self.regex_content.findall(content)
        else:
            if not self.regex_url:
                raise FatalError("Neither url nor content filter provided.")
            else:
                match = True

        interesting_content = bool(match)

        if not self.regex_url:
            next_urls = links
        else:
            for a in links:
                if self.regex_url.match(a):
                    if self.target_html:
                        if ural.could_be_html(a): next_urls.add(a)
                        else: ignored_urls.add(a)
                    else: next_urls.add(a)
                else:
                    ignored_urls.add(a)


        if (not interesting_content and not self.unteresting_continue) or job.depth + 1 > self.depth:
            next_urls = set()


        rep_obj = FocusResponse(
            interesting_content,
            ignored_urls
        )


        return (rep_obj, next_urls)

    # Iterable[str | CrawlTarget] | None
    def start(self):
        return self.urls
