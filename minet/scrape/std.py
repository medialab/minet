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


def iter_descendants_with_parent(element):
    for descendant in element.descendants:
        yield descendant.parent, descendant


def get_display_text(element):
    def accumulator():
        for parent, descendant in iter_descendants_with_parent(element):
            parent_display = get_element_display(parent)

            # print(
            #     parent_display,
            #     'string' if isinstance(descendant, NavigableString) else descendant.name,
            #     str(descendant).replace('\n', '\\n') if isinstance(descendant, NavigableString) else None
            # )

            if not isinstance(descendant, NavigableString):
                continue

            string = squeeze(descendant.strip())

            if string:
                if parent_display == 'block':
                    yield '\n' + string
                else:
                    yield ' ' + string

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
