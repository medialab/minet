# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from bs4 import BeautifulSoup

from minet.utils import load_definition
from minet.scrape.interpreter import interpret_scraper, tabulate
from minet.scrape.analysis import analyse, validate
from minet.scrape.exceptions import (
    ScraperNotTabularError,
    InvalidScraperError
)


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
        if not isinstance(definition, dict):
            definition = load_definition(definition)

        # Validating the definition
        errors = validate(definition)

        if errors:
            raise InvalidScraperError('scraper is invalid', validation_errors=errors)

        self.definition = definition

        # Analysis of the definition
        analysis = analyse(definition)

        self.headers = analysis.headers
        self.plural = analysis.plural
        self.output_type = analysis.output_type

    def __call__(self, html, context=None):
        return scrape(self.definition, html, context=context)


__all__ = ['Scraper', 'validate']
