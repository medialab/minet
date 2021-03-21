# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from bs4 import BeautifulSoup

from minet.utils import load_definition
from minet.scrape.interpreter import interpret_scraper, tabulate


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
        html=None if soup is html else html,
        context=context
    )


def headers_from_definition(scraper):
    tabulate = scraper.get('tabulate')

    if tabulate is not None:
        if not isinstance(tabulate, dict):
            return

        return tabulate.get('headers')

    fields = scraper.get('fields')

    if fields is None:
        return ['value']

    return list(scraper['fields'].keys())


class Scraper(object):
    def __init__(self, definition):
        self.definition = definition
        self.headers = headers_from_definition(definition)

    def __call__(self, html, context=None):
        return scrape(self.definition, html, context=context)

    @staticmethod
    def from_file(target):
        return Scraper(load_definition(target))
