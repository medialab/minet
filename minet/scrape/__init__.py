# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from bs4 import BeautifulSoup

from minet.utils import load_definition
from minet.scrape.interpreter import interpret_scraper, tabulate
from minet.scrape.analysis import headers_from_definition, validate


def ensure_soup(html_or_soup, engine='lxml'):
    is_already_soup = isinstance(html_or_soup, BeautifulSoup)

    if not is_already_soup:
        return BeautifulSoup(html_or_soup, engine)

    return html_or_soup


def scrape(scraper, html, engine='lxml', context=None):
    soup = ensure_soup(html)

    return interpret_scraper(
        scraper,
        soup,
        root=soup,
        context=context
    )


class Scraper(object):
    def __init__(self, definition):
        self.definition = definition
        self.headers = headers_from_definition(definition)

    def __call__(self, html, context=None):
        return scrape(self.definition, html, context=context)

    @staticmethod
    def from_file(target):
        return Scraper(load_definition(target))


__all__ = ['scrape', 'Scraper', 'validate']
