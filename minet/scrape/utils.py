# =============================================================================
# Minet Scraper Utils
# =============================================================================
#
# Miscellaneous helper functions used throughout the minet.scrape package.
#
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from functools import partial

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
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=XMLParsedAsHTMLWarning)
        return BeautifulSoup(html, engine)
