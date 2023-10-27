# =============================================================================
# Minet Scraper Utils
# =============================================================================
#
# Miscellaneous helper functions used throughout the minet.scrape package.
#
from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from minet.scrape.types import AnyScrapableTarget


from bs4 import BeautifulSoup, SoupStrainer
from functools import partial

from minet.scrape.soup import suppress_xml_parsed_as_html_warnings, WonderfulSoup
from minet.scrape.constants import SELECT_ALIASES, ITERATOR_ALIASES


def get_aliases(aliases, target, with_key=False):
    for alias in aliases:
        if alias in target:
            if with_key:
                return alias, target[alias]

            return target[alias]

    if with_key:
        return None, None

    return None


get_sel = partial(get_aliases, SELECT_ALIASES)
get_iterator = partial(get_aliases, ITERATOR_ALIASES)


def BeautifulSoupWithoutXHTMLWarnings(html, engine):
    with suppress_xml_parsed_as_html_warnings():
        return BeautifulSoup(html, engine)


def ensure_soup(
    html_or_soup: "AnyScrapableTarget",
    engine: str = "lxml",
    strainer: Optional[SoupStrainer] = None,
) -> Union[BeautifulSoup, WonderfulSoup]:
    if not isinstance(html_or_soup, (WonderfulSoup, BeautifulSoup)):
        return WonderfulSoup(html_or_soup, engine, parse_only=strainer)

    return html_or_soup
