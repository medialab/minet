from typing import Optional, Callable, Any, cast, Dict

import inspect
from casanova import RowWrapper
from bs4 import SoupStrainer

from minet.scrape.classes.base import ScraperBase
from minet.scrape.soup import WonderfulSoup
from minet.scrape.straining import strainer_from_css
from minet.scrape.utils import ensure_soup
from minet.scrape.types import AnyScrapableTarget


class FunctionScraper(ScraperBase):
    fn: Callable[[RowWrapper, WonderfulSoup], Any]
    fieldnames = None
    plural: bool
    tabular = True
    output_type = None
    strainer: Optional[SoupStrainer]

    def __init__(
        self,
        fn: Callable[[RowWrapper, WonderfulSoup], Any],
        strain: Optional[str] = None,
    ):
        self.fn = fn
        self.plural = inspect.isgeneratorfunction(fn)

        self.strainer = None

        if strain is not None:
            self.strainer = strainer_from_css(strain)

    def __call__(self, html: AnyScrapableTarget, context: Optional[Dict] = None):
        assert context is not None

        row = context["row"]
        soup = cast(WonderfulSoup, ensure_soup(html, strainer=self.strainer))

        return self.fn(row, soup)
