from typing import List, Optional

import warnings
from contextlib import contextmanager
from bs4 import Tag, BeautifulSoup

try:
    from bs4 import XMLParsedAsHTMLWarning
except ImportError:
    XMLParsedAsHTMLWarning = None


class MinetTag(Tag):
    def hello(self) -> None:
        print("hello")

    def select_one(self, css: str) -> Optional["MinetTag"]:
        return super().select_one(css)  # type: ignore


WONDERFUL_ELEMENT_CLASSES = {Tag: MinetTag}


class WonderfulSoup(BeautifulSoup, MinetTag):
    """
    A subclass of BeautifulSoup with some handy tricks such as selection
    wrangling, scraping utilities and better typings.
    """

    def __init__(self, markup: str, features: str = "lxml") -> None:
        super().__init__(markup, features, element_classes=WONDERFUL_ELEMENT_CLASSES)  # type: ignore


@contextmanager
def suppress_xml_parsed_as_html_warnings(bypass=False):
    try:
        if XMLParsedAsHTMLWarning is None or bypass:
            yield
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=XMLParsedAsHTMLWarning)
                yield
    finally:
        pass


if __name__ == "__main__":
    html = "<div><p>wonderful</p></div>"
    soup = WonderfulSoup(html)

    soup.hello()
    p = soup.select_one("p")

    assert p is not None

    p.hello()
