# =============================================================================
# Minet Scrapers Standard Library
# =============================================================================
#
# Collection of helpers, and depencies exposed to scraper evaluation.
#
import re
import json
import soupsieve
import dateparser
from urllib.parse import urljoin
from bs4 import NavigableString
from ebbe import with_next

from minet.utils import squeeze
from minet.scrape.constants import BLOCK_ELEMENTS


def is_block_element(element):
    if isinstance(element, NavigableString):
        return False

    return (
        element.name in BLOCK_ELEMENTS or
        element.name == 'html' or
        element.name == '[document]'
    )


def get_element_display(element):
    return 'block' if is_block_element(element) else 'inline'


# NOTE: could be optimized?
def get_block_parent(element):
    parent = element.parent

    while True:
        if parent is not None and is_block_element(parent):
            return parent

        parent = parent.parent


def get_display_text(element):

    def accumulator():
        previous_block_parent = None

        for descendant, next_descendant in with_next(element.descendants):
            if not isinstance(descendant, NavigableString):

                if descendant.name == 'br' or descendant.name == 'hr':
                    yield '\n'

                continue

            string = squeeze(descendant.strip())

            if not string:
                continue

            block_parent = get_block_parent(descendant)

            if block_parent != previous_block_parent:
                previous_block_parent = block_parent
                yield '\n'

            if string:
                yield string

            # TODO: if before or after inline element with space around, should add a whitespace

    return (''.join(accumulator())).strip()


def parse_date(formatted_date, lang='en'):
    try:
        parsed = dateparser.parse(
            formatted_date,
            languages=[lang]
        )
    except ValueError:
        return None

    return parsed.isoformat().split('.', 1)[0]


def get_default_evaluation_context():
    return {

        # Dependencies
        'json': json,
        'urljoin': urljoin,
        're': re,
        'soupsieve': soupsieve,

        # Helpers
        'parse_date': parse_date
    }
