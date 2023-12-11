from typing import Union, Optional, List, Dict, Any

from bs4 import BeautifulSoup, SoupStrainer

from minet.scrape.soup import WonderfulSoup
from minet.scrape.analysis import ScraperAnalysisOutputType

AnyScrapableTarget = Union[str, WonderfulSoup, BeautifulSoup]


class ScraperBase(object):
    fieldnames: Optional[List[str]]
    plural: bool
    tabular: bool
    output_type: Optional[ScraperAnalysisOutputType]
    strainer: Optional[SoupStrainer]

    @property
    def singular(self) -> bool:
        return not self.plural

    def __repr__(self):
        return "<{name} plural={plural} output_type={output_type} strain={strain} fieldnames={fieldnames!r}>".format(
            name=self.__class__.__name__,
            plural=self.plural,
            strain=getattr(self.strainer, "css", None) if self.strainer else None,
            output_type=self.output_type,
            fieldnames=self.fieldnames,
        )

    def __call__(self, html: AnyScrapableTarget, context: Optional[Dict] = None) -> Any:
        raise NotImplementedError

    def items(self, html: AnyScrapableTarget, context: Optional[Dict] = None):
        result = self.__call__(html, context=context)

        if result is None:
            return

        if not self.plural:
            yield result
            return

        yield from result
