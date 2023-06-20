from typing import List, Optional, overload, cast
from minet.types import Literal

import warnings
from contextlib import contextmanager
from bs4 import Tag, BeautifulSoup, SoupStrainer

from minet.scrape.std import get_display_text

try:
    from bs4 import XMLParsedAsHTMLWarning
except ImportError:
    XMLParsedAsHTMLWarning = None


class SelectionError(Exception):
    pass


class MinetTag(Tag):
    @overload
    def select_one(
        self, css: str, *args, strict: Literal[False] = ..., **kwargs
    ) -> Optional["MinetTag"]:
        ...

    @overload
    def select_one(
        self, css: str, *args, strict: Literal[True] = ..., **kwargs
    ) -> "MinetTag":
        ...

    def select_one(
        self, css: str, *args, strict: bool = False, **kwargs
    ) -> Optional["MinetTag"]:
        elem = super().select_one(css, *args, **kwargs)

        if strict and elem is None:
            raise SelectionError(css)

        return cast(MinetTag, elem)

    def select(self, css: str, *args, **kwargs) -> List["MinetTag"]:
        css = css.replace(":contains(", ":-soup-contains(")

        return cast(List["MinetTag"], super().select(css, *args, **kwargs))

    def get_text(self) -> str:
        return super().get_text().strip()

    def get_display_text(self) -> str:
        return get_display_text(self)

    def get_html(self) -> str:
        return self.decode_contents().strip()

    def get_inner_html(self) -> str:
        return self.get_html()

    def get_outer_html(self) -> str:
        return str(self).strip()


WONDERFUL_ELEMENT_CLASSES = {Tag: MinetTag}


class WonderfulSoup(BeautifulSoup, MinetTag):
    """
    A subclass of BeautifulSoup with some handy tricks such as selection
    wrangling, scraping utilities and better typings.
    """

    def __init__(
        self,
        markup: str,
        features: str = "lxml",
        parse_only: Optional[SoupStrainer] = None,
    ) -> None:
        super().__init__(markup, features, element_classes=WONDERFUL_ELEMENT_CLASSES, parse_only=parse_only)  # type: ignore


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
