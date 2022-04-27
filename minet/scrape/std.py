# =============================================================================
# Minet Scrapers Standard Library
# =============================================================================
#
# Collection of helpers, and depencies exposed to scraper evaluation.
#
import re
import json
import soupsieve
from urllib.parse import urljoin
from bs4 import Tag, NavigableString

from minet.utils import parse_date
from minet.scrape.constants import BLOCK_ELEMENTS, CONTENT_BLOCK_ELEMENTS


LEADING_WHITESPACE_RE = re.compile(r"^\s")
TRAILING_WHITESPACE_RE = re.compile(r"\s$")
LINE_STRIPPER_RE = re.compile(r"\n +| +\n")
PARAGRAPH_NORMALIZER_RE = re.compile(r"\n{3,}")
SPACE_SQUEEZER_RE = re.compile(r" {2,}")
WHITESPACE_SQUEEZER_RE = re.compile(r"\s{2,}")
CDATA_STRIPPER_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.I)


def has_leading_whitespace(string):
    return LEADING_WHITESPACE_RE.match(string) is not None


def has_trailing_whitespace(string):
    return TRAILING_WHITESPACE_RE.search(string) is not None


def unescape_cdata(string):
    return CDATA_STRIPPER_RE.sub(r"\1", string)


def is_block_element(element):
    if isinstance(element, NavigableString):
        return False

    return (
        element.name in BLOCK_ELEMENTS
        or element.name == "html"
        or element.name == "[document]"
    )


def is_inline_element(element):
    return not is_block_element(element)


def get_element_display(element):
    return "block" if is_block_element(element) else "inline"


# NOTE: could be optimized?
def get_block_parent(element):
    parent = element.parent

    while True:
        if parent is not None and is_block_element(parent):
            return parent

        parent = parent.parent


def get_previous_sibling(element):
    while element.previous_sibling is not None:
        if isinstance(element.previous_sibling, Tag):
            return element.previous_sibling

        element = element.previous_sibling

    return None


def get_display_text(element):
    if isinstance(element, list):
        pieces = (get_display_text(el) for el in element)

        return "\n\n".join(piece for piece in pieces if piece.strip())

    def accumulator():
        previous_block_parent = None
        last_string = None

        for descendant in element.descendants:
            if not isinstance(descendant, NavigableString):

                if descendant.name == "br":
                    yield "\n"

                elif descendant.name == "hr":
                    yield "\n\n"

                elif descendant.name in CONTENT_BLOCK_ELEMENTS:
                    yield "\n"

                else:
                    sibling = get_previous_sibling(descendant)

                    if sibling:
                        if sibling.name in CONTENT_BLOCK_ELEMENTS:
                            yield "\n"
                        else:
                            yield " "

                continue

            if descendant.parent.name == "pre":
                yield "\n" + str(descendant)
                continue

            string = WHITESPACE_SQUEEZER_RE.sub(" ", descendant.strip("\n"))

            if not string:
                continue

            block_parent = get_block_parent(descendant)

            if block_parent is not previous_block_parent:
                previous_block_parent = block_parent
                yield "\n"

            if last_string and last_string.endswith(" "):
                string = string.lstrip()

            string = unescape_cdata(string)

            if string:
                yield string

            last_string = string

    result = "".join(accumulator())
    result = LINE_STRIPPER_RE.sub("\n", result)
    result = PARAGRAPH_NORMALIZER_RE.sub("\n\n", result)
    result = SPACE_SQUEEZER_RE.sub(" ", result)
    result = result.strip()

    return result


def get_default_evaluation_context():
    return {
        # Dependencies
        "json": json,
        "urljoin": urljoin,
        "re": re,
        "soupsieve": soupsieve,
        # Helpers
        "get_display_text": get_display_text,
        "parse_date": parse_date,
    }
