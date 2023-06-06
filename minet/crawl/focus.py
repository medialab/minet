import re
import ural
import warnings
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin

from minet.cli.exceptions import FatalError
from minet.web import looks_like_html
from minet.crawl.types import CrawlJob
from minet.extraction import extract
from minet.web import Response
from minet.crawl.spiders import Spider

class FocusResponse:
    def __init__(self, interesting, regex_match_size, ignored_url) -> None:
        self.interesting = interesting
        self.regex_match_size = regex_match_size
        self.ignored_url = ignored_url

class FocusSpider(Spider):

    def clean_url(self, origin, url):
        url = urljoin(origin, url)
        return ural.normalize_url(url)

    def __init__(
        self,
        start_urls,
        max_depth = 3,
        regex_content = None,
        regex_url = None,
        uninteresting_continue = False,
        perform_on_html = True,
        only_target_html_page = True):

        try:
            int(max_depth)
            self.depth = int(max_depth)
        except:
            raise TypeError("max depth needs to be an integer")

        self.urls = start_urls
        self.regex_content = re.compile(regex_content, re.I) if regex_content else None
        self.regex_url = re.compile(regex_url, re.I) if regex_url else None
        self.extraction = not perform_on_html
        self.unteresting_continue = uninteresting_continue
        self.target_html = only_target_html_page

    def __call__(self, job: CrawlJob, response: Response):

        # Return variables
        interesting_content = False
        next_urls = set()
        ignored_urls = set()

        end_url = response.end_url

        html = response.body
        if self.target_html and not looks_like_html(html):
            return (FocusResponse(False, 0, None), [])
        if not response.is_text or not html:
            return (FocusResponse(False, 0, None), [])

        html = response.text()
        content = html

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


        bs = response.soup(ignore_xhtml_warning=True, strainer=SoupStrainer("a")).find_all("a")
        links = set(self.clean_url(end_url, a.get('href')) for a in bs if a.get('href'))

        if self.regex_content:
            match = self.regex_content.findall(content)
        else:
            if not self.regex_url:
                raise FatalError("Neither url nor content filter provided.")
            else:
                match = True

        interesting_size = len(match) if match else 0
        interesting_content = bool(match)

        if not self.regex_url:
            next_urls = links
        else:
            for a in links:
                if self.regex_url.search(a):
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
            interesting_size,
            ignored_urls
        )

        return (rep_obj, next_urls)

    def start(self):
        self.urls = list(self.urls)
        return self.urls
