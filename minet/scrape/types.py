from typing import Union, Optional, List, Dict, Any

from bs4 import BeautifulSoup, SoupStrainer
from casanova import CSVSerializer

from minet.scrape.soup import WonderfulSoup
from minet.scrape.analysis import ScraperAnalysisOutputType
from minet.scrape.exceptions import ScraperNotTabularError

AnyScrapableTarget = Union[str, WonderfulSoup, BeautifulSoup]


class ScraperBase(object):
    fieldnames: Optional[List[str]]
    plural: bool
    output_type: ScraperAnalysisOutputType
    serializer: CSVSerializer
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

    def as_csv_rows(
        self,
        html: AnyScrapableTarget,
        context: Optional[Dict] = None,
        plural_separator="|",
    ):
        if self.fieldnames is None:
            raise ScraperNotTabularError

        def generator():
            result = self.__call__(html, context=context)

            if result is None:
                return

            if not self.plural:
                result = [result]

            for item in result:
                if isinstance(item, dict):
                    assert self.fieldnames

                    item = self.serializer.serialize_dict_row(
                        item, self.fieldnames, plural_separator=plural_separator
                    )
                else:
                    item = [self.serializer(item, plural_separator=plural_separator)]

                yield item

        return generator()

    def as_csv_dict_rows(
        self,
        html: AnyScrapableTarget,
        context: Optional[Dict] = None,
        plural_separator="|",
    ):
        if self.fieldnames is None:
            raise ScraperNotTabularError

        def generator():
            result = self.__call__(html, context=context)

            if result is None:
                return

            if not self.plural:
                result = [result]

            for item in result:
                if isinstance(item, dict):
                    for k, v in item.items():
                        item[k] = self.serializer(v, plural_separator=plural_separator)
                else:
                    item = {
                        "value": self.serializer(
                            item, plural_separator=plural_separator
                        )
                    }

                yield item

        return generator()

    def as_records(self, html: AnyScrapableTarget, context: Optional[Dict] = None):
        result = self.__call__(html, context=context)

        if result is None:
            return

        if not self.plural:
            yield result
            return

        yield from result
