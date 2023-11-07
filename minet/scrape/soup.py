import re
from typing import List, Optional, cast, overload

import warnings
from contextlib import contextmanager
from bs4 import Tag, BeautifulSoup, SoupStrainer

from minet.scrape.std import get_display_text

try:
    from bs4 import XMLParsedAsHTMLWarning
except ImportError:
    XMLParsedAsHTMLWarning = None

WHITESPACE_RE = re.compile(r"\s+")


class SelectionError(Exception):
    pass


def extract(elem: "MinetTag", target: Optional[str]) -> Optional[str]:
    if target is None or target == "text":
        return elem.get_text()

    if target == "html" or target == "inner_html":
        return elem.get_html()

    if target == "outer_html":
        return elem.get_outer_html()

    if target == "display_text":
        return elem.get_display_text()

    return cast(Optional[str], elem.get(target))


class MinetTag(Tag):
    def force_select_one(self, css: str, *args, **kwargs) -> "MinetTag":
        elem = super().select_one(css, *args, **kwargs)

        if elem is None:
            raise SelectionError(css)

        return cast(MinetTag, elem)

    def select_one(self, css: str, *args, **kwargs) -> Optional["MinetTag"]:
        return cast(Optional["MinetTag"], super().select_one(css, *args, **kwargs))

    def select(self, css: str, *args, **kwargs) -> List["MinetTag"]:
        css = css.replace(":contains(", ":-soup-contains(")

        return cast(List["MinetTag"], super().select(css, *args, **kwargs))

    def scrape_one(
        self, css: str, target: Optional[str] = None, strict: bool = False
    ) -> Optional[str]:
        elem = self.select_one(css)

        if elem is None:
            if strict:
                raise SelectionError(css)

            return None

        return extract(elem, target)

    def scrape(self, css: str, target: Optional[str] = None) -> List[str]:
        output = []

        for elem in self.select(css):
            value = extract(elem, target)

            if value is not None:
                output.append(value)

        return output

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

    def __getitem__(self, name: str) -> str:
        return cast(str, super().__getitem__(name))

    @overload
    def get(self, name: str, default: str = ...) -> str:
        ...

    @overload
    def get(self, name: str, default: None = ...) -> Optional[str]:
        ...

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        return cast(Optional[str], super().get(name, default))

    def get_list(self, name: str) -> List[str]:
        value = super().get(name)

        if not value:
            return []

        return WHITESPACE_RE.split(cast(str, value).strip())


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
        super().__init__(markup, features, element_classes=WONDERFUL_ELEMENT_CLASSES, parse_only=parse_only, multi_valued_attributes=None)  # type: ignore


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
