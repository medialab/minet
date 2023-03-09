# =============================================================================
# Minet Scrape Module
# =============================================================================
#
# Module exposing utilities related to minet's scraping DSL.
#
from typing import Dict, Optional, Union, List

from bs4 import BeautifulSoup, SoupStrainer
from casanova import CSVSerializer

from minet.types import AnyFileTarget
from minet.fs import load_definition
from minet.scrape.interpreter import interpret_scraper
from minet.scrape.analysis import analyse, validate, ScraperAnalysisOutputType
from minet.scrape.straining import strainer_from_css
from minet.scrape.exceptions import ScraperNotTabularError, InvalidScraperError


def ensure_soup(
    html_or_soup: Union[str, BeautifulSoup],
    engine: str = "lxml",
    strainer: Optional[SoupStrainer] = None,
) -> BeautifulSoup:
    is_already_soup = isinstance(html_or_soup, BeautifulSoup)

    if not is_already_soup:
        return BeautifulSoup(html_or_soup, engine, parse_only=strainer)

    return html_or_soup


def scrape(
    scraper: Dict,
    html: Union[str, BeautifulSoup],
    engine: str = "lxml",
    context: Optional[Dict] = None,
    strainer: Optional[SoupStrainer] = None,
):
    soup = ensure_soup(html, strainer=strainer, engine=engine)

    return interpret_scraper(scraper, soup, root=soup, context=context)


class Scraper(object):
    definition: Dict
    fieldnames: Optional[List[str]]
    plural: bool
    output_type: ScraperAnalysisOutputType

    def __init__(
        self, definition: Union[Dict, AnyFileTarget], strain: Optional[str] = None
    ):
        if not isinstance(definition, dict):
            definition = load_definition(definition)

        # Validating the definition
        errors = validate(definition)

        if errors:
            raise InvalidScraperError("scraper is invalid", validation_errors=errors)

        self.definition = definition

        # Analysis of the definition
        analysis = analyse(definition)

        self.fieldnames = analysis.fieldnames
        self.plural = analysis.plural
        self.output_type = analysis.output_type

        # Serializer
        self.serializer = CSVSerializer()

        # Strainer
        self.strainer = None

        if strain is not None:
            self.strainer = strainer_from_css(strain)

    def __repr__(self):
        return "<{name} plural={plural} output_type={output_type} strain={strain} fieldnames={fieldnames!r}>".format(
            name=self.__class__.__name__,
            plural=self.plural,
            strain=self.strainer.css if self.strainer else None,
            output_type=self.output_type,
            fieldnames=self.fieldnames,
        )

    def __call__(self, html: Union[str, BeautifulSoup], context: Optional[Dict] = None):
        return scrape(self.definition, html, context=context, strainer=self.strainer)

    def as_csv_dict_rows(
        self,
        html: Union[str, BeautifulSoup],
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

    def as_records(
        self, html: Union[str, BeautifulSoup], context: Optional[Dict] = None
    ):
        result = self.__call__(html, context=context)

        if result is None:
            return

        if not self.plural:
            yield result
            return

        yield from result


__all__ = ["Scraper", "validate"]
