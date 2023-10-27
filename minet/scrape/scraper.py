from typing import Dict, Optional, Union, List

from bs4 import SoupStrainer
from casanova import CSVSerializer

from minet.types import AnyFileTarget
from minet.fs import load_definition
from minet.scrape.interpreter import interpret_scraper
from minet.scrape.analysis import analyse, validate, ScraperAnalysisOutputType
from minet.scrape.straining import strainer_from_css
from minet.scrape.exceptions import InvalidScraperError
from minet.scrape.utils import ensure_soup
from minet.scrape.types import AnyScrapableTarget, ScraperBase


def scrape(
    scraper: Dict,
    html: AnyScrapableTarget,
    engine: str = "lxml",
    context: Optional[Dict] = None,
    strainer: Optional[SoupStrainer] = None,
):
    soup = ensure_soup(html, strainer=strainer, engine=engine)

    return interpret_scraper(scraper, soup, root=soup, context=context)


class Scraper(ScraperBase):
    definition: Dict
    fieldnames: Optional[List[str]]
    plural: bool
    output_type: ScraperAnalysisOutputType
    serializer: CSVSerializer
    strainer: Optional[SoupStrainer]

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

    def __call__(self, html: AnyScrapableTarget, context: Optional[Dict] = None):
        return scrape(self.definition, html, context=context, strainer=self.strainer)
