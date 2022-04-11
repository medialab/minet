# =============================================================================
# Minet Scraper Straining
# =============================================================================
#
# Function related to automatic bs4 SoupStrainer creation from simple
# CSS selectors.
#
import re
from bs4 import SoupStrainer
from soupsieve import SelectorSyntaxError
from soupsieve.css_parser import CSSParser

from minet.scrape.exceptions import CSSSelectorTooComplex, InvalidCSSSelectorError

WHITESPACE_RE = re.compile(r"\s+")


def match_selector(selector, tag, attrs):

    # Checking tag name
    if selector.tag.name != "*" and tag != selector.tag.name:
        return False

    # Checking id
    if selector.ids and attrs.get("id") not in selector.ids:
        return False

    # Checking class
    if selector.classes:
        classes = WHITESPACE_RE.split(attrs.get("class", ""))

        # NOTE: this is quadratic but probably faster than using sets in most cases?
        if not any(c in selector.classes for c in classes):
            return False

    # Checking attributes
    for target in selector.attributes:
        if target.attribute not in attrs:
            return False

        if target.pattern:
            if not target.pattern.match(attrs[target.attribute]):
                return False

    return True


def strainer_from_css(css, ignore_relations=False):
    try:
        selector_list = CSSParser(css).process_selectors()
    except (SelectorSyntaxError, NotImplementedError) as e:
        raise InvalidCSSSelectorError(reason=e)

    usable_selectors = []

    for selector in selector_list:
        if selector.selectors or selector.nth:
            raise CSSSelectorTooComplex

        if not ignore_relations:
            if len(selector.relation) != 0:
                raise CSSSelectorTooComplex

            usable_selectors.append(selector)
        else:
            while selector.relation:
                selector = selector.relation[0]

            usable_selectors.append(selector)

    def strainer_function(tag, attrs):
        return any(
            match_selector(selector, tag, attrs) for selector in usable_selectors
        )

    strainer = SoupStrainer(strainer_function)

    setattr(strainer, "css", css)

    return strainer
