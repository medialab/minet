from typing import (
    Union,
    Optional,
    Callable,
    Any,
    cast,
    Dict,
    List,
    get_origin,
    get_args,
    get_type_hints,
)

import inspect

from casanova import RowWrapper
from bs4 import SoupStrainer

from minet.scrape.classes.base import ScraperBase
from minet.scrape.soup import WonderfulSoup
from minet.scrape.straining import strainer_from_css
from minet.scrape.utils import ensure_soup
from minet.scrape.types import AnyScrapableTarget


def infer_fieldnames_from_function_return_type(fn: Callable) -> Optional[List[str]]:
    if not callable(fn):
        raise TypeError

    return_type = get_type_hints(fn)["return"]

    origin = get_origin(return_type)

    if origin is Union:
        args = get_args(return_type)

        # Optionals
        if len(args) == 2:
            if args[1] is type(None):
                return_type = args[0]

    if return_type in (str, int, float, bool, type(None)):
        return ["value"]

    return None


class FunctionScraper(ScraperBase):
    fn: Union[str, Callable[[RowWrapper, WonderfulSoup], Any]]
    fieldnames = None
    plural: bool
    tabular = True
    output_type = None
    strainer: Optional[SoupStrainer]

    def __init__(
        self,
        fn: Union[str, Callable[[RowWrapper, WonderfulSoup], Any]],
        strain: Optional[str] = None,
    ):
        # NOTE: closures cannot be pickled without using third-party library `dill`.
        self.fn = fn
        self.plural = inspect.isgeneratorfunction(fn)

        self.strainer = None

        if strain is not None:
            self.strainer = strainer_from_css(strain)

    def __call__(self, html: AnyScrapableTarget, context: Optional[Dict] = None):
        assert context is not None

        row = context["row"]
        soup = cast(WonderfulSoup, ensure_soup(html, strainer=self.strainer))

        if isinstance(self.fn, str):
            return eval(self.fn, {"row": row, "soup": soup}, None)

        return self.fn(row, soup)
