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


def strainer_from_css(css):
    selector_list = CSSParser(css).process_selectors()

    if len(selector_list) > 1:
        raise ScrapeCSSSelectorTooComplex

    selector = selector_list[0]

    if len(selector.relation) != 0:
        raise ScrapeCSSSelectorTooComplex

    tag_name = selector.tag.name

    def strainer_function(tag, attrs):

        if tag_name is not None and tag != tag_name:
            return False

        return True

    return SoupStrainer(strainer_function)
