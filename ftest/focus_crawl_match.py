from minet.crawl import Crawler, CrawlJob, CrawlResult
from minet.crawl.focus import FocusSpider
from minet.cli.console import console
from minet.web import request
from minet.scrape.typical import UrlsScraper
from minet.extraction import extract
from urllib.parse import urljoin
import minet.executors

import hashlib
import ural
import urllib3
import casanova
import os.path
import csv
import hashlib
import collections
import sys
import ural
import urllib.parse
import re


def hash(url):
    return hashlib.md5(url.encode()).hexdigest()

def test(
    resp,
    regex: re.Pattern,
    depth = 0,
    on_bare_html = True,
    a_with_bs = False,
    ):

    url = resp.end_url

    if not resp.is_html:
        return (False, None)
    html = resp.text()

    # Handling relevant

    if on_bare_html:
        content = html
    else:
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

    match = regex.findall(content)
    relevant = bool(match)

    # Handling links
    links = set(ural.urls_from_text(html))

    if a_with_bs:
        bs = r.soup()
        others = UrlsScraper().scrape(bs)
        links.update(others)
    else:
        others = ural.urls_from_html(html)
        links.update(others)

    pertinent = 0
    if depth == 0:
        pool = minet.executors.HTTPThreadPoolExecutor()
        urls = [urljoin(url, l) for l in links]
        for r in pool.request(urls):
            if r.response:
                rr = test(
                    r.response,
                    regex,
                    depth+1,
                    on_bare_html,
                    a_with_bs)
                if rr:
                    (i, r) = rr
                    if i: pertinent += 1

    return (relevant, {
        "url": url,
        "relevant": relevant,
        "on html": on_bare_html,
        "using bs": a_with_bs,
        "nexts": len(links),
        "pertinent": pertinent,
    })

def run_test(filename, export, regex, html, bs):
    with open(filename) as file:
        csv = casanova.reader(file)
        with open(export, "a") as export:
            wrt = casanova.writer(export, fieldnames=[
                "url",
                "relevant",
                "on html",
                "using bs",
                "nexts",
                "pertinent"
            ])
            urls = []
            for f in csv:
                """
                (i, r) = test(f[3], regex, 0, html, bs)
                if r:
                    wrt.writerow(r.values())
                """
                urls.append(f[3])
            pool = minet.executors.HTTPThreadPoolExecutor()
            for r in pool.request(urls):
                if r.response:
                    (i, res) = test(r.response, regex, 0, html, bs)
                    if res:
                        wrt.writerow(res.values())
                        export.flush()



REGEX = re.compile(r"(?:[Pp]esticide|[Ff]ongicide|[Gg]lypho|[Rr]oundup|[Hh]erbicide|SDHI|sdhi|[Cc]hlord[ée]cone|[Ii]secticide|[Nn][ée]onicotino[ïi]de|[Dd]esherbant|[Pp]hyto)")


run_test(
    "../pesticides.csv",
    "../pesticides_export_match.csv",
    REGEX,
    html=True,
    bs=False
)

# Test result
#


