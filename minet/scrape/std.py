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
from minet.scrape.constants import BLOCK_ELEMENTS, CONTENT_BLOCK_ELEMENTS


LEADING_WHITESPACE_RE = re.compile(r'^\s')
TRAILING_WHITESPACE_RE = re.compile(r'\s$')
LINE_STRIPPER_RE = re.compile(r'\n +')


def has_leading_whitespace(string):
    return LEADING_WHITESPACE_RE.match(string) is not None


def has_trailing_whitespace(string):
    return TRAILING_WHITESPACE_RE.search(string) is not None


def is_block_element(element):
    if isinstance(element, NavigableString):
        return False

    return (
        element.name in BLOCK_ELEMENTS or
        element.name == 'html' or
        element.name == '[document]'
    )


def is_inline_element(element):
    return not is_block_element(element)


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
        last_string = None

        for descendant in element.descendants:
            if not isinstance(descendant, NavigableString):

                if descendant.name == 'br':
                    yield '\n'

                elif descendant.name == 'hr':
                    yield '\n\n'

                continue

            string = squeeze(descendant.strip('\n'))

            if not string:
                continue

            block_parent = get_block_parent(descendant)

            if block_parent is not previous_block_parent:
                previous_block_parent = block_parent
                yield '\n'

            if last_string and last_string.endswith(' '):
                string = string.lstrip()

            if string:
                yield string

            last_string = string

    result = ''.join(accumulator())
    result = result.strip()
    result = LINE_STRIPPER_RE.sub('\n', result)

    return result


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
