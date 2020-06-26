# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from bs4 import BeautifulSoup

from minet.utils import load_definition
from minet.scrape.apply import apply_scraper, tabulate


def scrape(scraper, html, engine='lxml', context=None):
    is_already_soup = isinstance(html, BeautifulSoup)

    if not is_already_soup:
        soup = BeautifulSoup(html, engine)
    else:
        soup = html

    return apply_scraper(
        scraper,
        soup,
        root=soup,
        html=str(soup) if is_already_soup else html,
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
