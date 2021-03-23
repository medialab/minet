# =============================================================================
# Minet Scraper Straining
# =============================================================================
#
# Function related to automatic bs4 SoupStrainer creation from simple
# CSS selectors.
#
from bs4 import SoupStrainer
from soupsieve.css_parser import CSSParser

from minet.scrape.exceptions import ScrapeCSSSelectorTooComplex


def match_selector(selector, tag, attrs):

    # Checking tag name
    if selector.tag.name != '*' and tag != selector.tag.name:
        return False

    # Checking id
    if selector.ids and attrs.get('id') not in selector.ids:
        return False

    return True


# TODO: test null selector or *

def strainer_from_css(css):
    if not css:
        raise TypeError('expecting a css selector but got empty value or string')

    selector_list = CSSParser(css).process_selectors()

    for selector in selector_list:
        if len(selector.relation) != 0:
            raise ScrapeCSSSelectorTooComplex

    def strainer_function(tag, attrs):
        return any(
            match_selector(selector, tag, attrs)
            for selector in selector_list
        )

    return SoupStrainer(strainer_function)
