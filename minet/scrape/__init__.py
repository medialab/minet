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


def format_value_for_csv(value, plural_separator='|'):
    if isinstance(value, list):
        return plural_separator.join(str(v) for v in value)

    if isinstance(value, bool):
        return 'true' if value else 'false'

    return value


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

    def as_csv_dict_rows(self, html, context=None, plural_separator='|'):
        if self.headers is None:
            raise ScraperNotTabularError

        def generator():

            result = scrape(self.definition, html, context=context)

            if not self.plural:
                result = [result]

            for item in result:
                if isinstance(item, dict):
                    for k, v in item.items():
                        item[k] = format_value_for_csv(v, plural_separator=plural_separator)
                else:
                    item = {'value': format_value_for_csv(item, plural_separator=plural_separator)}

                yield item

        return generator()


__all__ = ['Scraper', 'validate']
