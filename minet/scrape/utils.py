# =============================================================================
# Minet Scraper Utils
# =============================================================================
#
# Miscellaneous helper functions used throughout the minet.scrape package.
#
import json
import yaml
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from os import PathLike
from functools import partial
from ebbe.decorators import with_defer

from minet.scrape.constants import SELECT_ALIASES, ITERATOR_ALIASES
from minet.exceptions import DefinitionInvalidFormatError


@with_defer()
def load_definition(f, defer, encoding="utf-8"):
    if isinstance(f, (str, PathLike)):
        path = f
        f = open(path, encoding=encoding)
        defer(f.close)
    else:
        path = f.name

    if path.endswith(".json"):
        definition = json.load(f)

    elif path.endswith(".yml") or path.endswith(".yaml"):
        definition = yaml.safe_load(f)

    else:
        raise DefinitionInvalidFormatError

    return definition


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
