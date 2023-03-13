# =============================================================================
# Minet Spiders
# =============================================================================
#
#
from typing import (
    cast,
    Any,
    Optional,
    List,
    Tuple,
    TypeVar,
    Union,
    Callable,
    Dict,
    Iterator,
    Iterable,
    Generic,
)
from minet.types import TypedDict, NotRequired

from urllib.parse import urljoin
from bs4 import BeautifulSoup

from minet.crawl.types import (
    UrlOrCrawlJob,
    CrawlJob,
    CrawlJobDataType,
    CrawlJobOutputDataType,
)
from minet.types import AnyFileTarget
from minet.fs import load_definition
from minet.scrape import Scraper
from minet.web import Response
from minet.utils import PseudoFStringFormatter

FORMATTER = PseudoFStringFormatter()

T = TypeVar("T")


def ensure_list(value: Union[T, List[T]]) -> List[T]:
    if not isinstance(value, list):
        return [value]
    return value


SpiderNextJobs = Optional[Iterable[CrawlJob[CrawlJobDataType]]]
SpiderResult = Tuple[CrawlJobOutputDataType, SpiderNextJobs[CrawlJobDataType]]


class Spider(Generic[CrawlJobDataType, CrawlJobOutputDataType]):
    def start_jobs(self) -> Optional[Iterable[UrlOrCrawlJob[CrawlJobDataType]]]:
        return None

    def __call__(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> SpiderResult[CrawlJobOutputDataType, CrawlJobDataType]:
        raise NotImplementedError

    def __repr__(self):
        class_name = self.__class__.__name__

        return "<%(class_name)s>" % {"class_name": class_name}


FunctionSpiderCallable = Callable[
    [CrawlJob[CrawlJobDataType], Response],
    SpiderResult[CrawlJobOutputDataType, CrawlJobDataType],
]


class FunctionSpider(Spider[CrawlJobDataType, CrawlJobOutputDataType]):
    fn: FunctionSpiderCallable[CrawlJobDataType, CrawlJobOutputDataType]

    def __init__(
        self,
        fn: FunctionSpiderCallable[CrawlJobDataType, CrawlJobOutputDataType],
        start_jobs: Optional[Iterable[UrlOrCrawlJob[CrawlJobDataType]]] = None,
    ):
        self.fn = fn
        self.__start_jobs = start_jobs

    def start_jobs(self) -> Optional[Iterable[UrlOrCrawlJob[CrawlJobDataType]]]:
        return self.__start_jobs

    def __call__(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> SpiderResult[CrawlJobOutputDataType, CrawlJobDataType]:
        return self.fn(job, response)


class DefinitionSpiderOutput(Generic[CrawlJobOutputDataType]):
    __slots__ = ("default", "named")

    def __init__(self):
        self.default = None
        self.named = {}


class DefinitionSpiderTarget(TypedDict, Generic[CrawlJobDataType]):
    url: str
    spider: NotRequired[str]
    data: NotRequired[CrawlJobDataType]


class DefinitionSpider(
    Spider[CrawlJobDataType, DefinitionSpiderOutput[CrawlJobOutputDataType]]
):
    definition: Dict[str, Any]
    next_definition: Optional[Dict[str, Any]]
    max_depth: int
    scraper: Optional[Scraper]
    scrapers: Dict[str, Scraper]
    next_scraper: Optional[Scraper]
    next_scrapers: Dict[str, Scraper]

    def __init__(self, definition: Union[AnyFileTarget, Dict[str, Any]]):

        if not isinstance(definition, dict):
            definition = load_definition(definition)

        definition = cast(Dict[str, Any], definition)

        # Descriptors
        self.definition = definition
        self.next_definition = definition.get("next")

        # Settings
        self.max_depth = definition.get("max_depth", float("inf"))

        # Scrapers
        self.scraper = None
        self.scrapers = {}
        self.next_scraper = None
        self.next_scrapers = {}

        if "scraper" in definition:
            self.scraper = Scraper(definition["scraper"])

        if "scrapers" in definition:
            for name, scraper in definition["scrapers"].items():
                self.scrapers[name] = Scraper(scraper)

        if self.next_definition is not None:
            if "scraper" in self.next_definition:
                self.next_scraper = Scraper(self.next_definition["scraper"])

            if "scrapers" in self.next_definition:
                for name, scraper in self.next_definition["scrapers"].items():
                    self.next_scrapers[name] = Scraper(scraper)

    def start_jobs(self) -> Iterable[UrlOrCrawlJob[CrawlJobDataType]]:

        # TODO: possibility to name this as jobs and get additional metadata
        start_urls = ensure_list(self.definition.get("start_url", [])) + ensure_list(
            self.definition.get("start_urls", [])
        )

        for url in start_urls:
            yield url

    def __scrape(
        self, job: CrawlJob[CrawlJobDataType], response: Response, soup: BeautifulSoup
    ) -> DefinitionSpiderOutput[CrawlJobOutputDataType]:
        scraped = DefinitionSpiderOutput[CrawlJobOutputDataType]()

        context = {"url": job.url}

        if self.scraper is not None:
            scraped.default = self.scraper(soup, context=context)

        for name, scraper in self.scrapers.items():
            scraped.named[name] = scraper(soup, context=context)

        return scraped

    def __job_from_target(
        self,
        current_url: str,
        target: Union[str, DefinitionSpiderTarget[CrawlJobDataType]],
    ) -> CrawlJob[CrawlJobDataType]:
        if isinstance(target, str):
            return CrawlJob(url=urljoin(current_url, target))

        else:

            # TODO: validate target
            return CrawlJob(
                url=urljoin(current_url, target["url"]),
                spider=target.get("spider"),
                data=target.get("data"),
            )

    def __next_targets(
        self, response: Response, soup: BeautifulSoup
    ) -> Iterator[Union[str, DefinitionSpiderTarget[CrawlJobDataType]]]:

        # Scraping next results
        if self.next_scraper is not None:
            scraped = self.next_scraper(soup)

            if scraped is not None:
                if isinstance(scraped, list):
                    yield from scraped
                else:
                    yield scraped

        if self.next_scrapers:
            for scraper in self.next_scrapers.values():
                scraped = scraper(soup)

                if scraped is not None:
                    if isinstance(scraped, list):
                        yield from scraped
                    else:
                        yield scraped

        # Formatting next url
        if self.next_definition is not None and "format" in self.next_definition:
            yield FORMATTER.format(self.next_definition["format"])

    def __next_jobs(
        self, job: CrawlJob[CrawlJobDataType], response: Response, soup: BeautifulSoup
    ):
        if not self.next_definition:
            return

        assert job.depth is not None

        next_depth = job.depth + 1

        if next_depth > self.max_depth:
            return

        for target in self.__next_targets(response, soup):
            yield self.__job_from_target(response.url, target)

    def __call__(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> SpiderResult[DefinitionSpiderOutput[CrawlJobOutputDataType], CrawlJobDataType]:
        soup = response.soup()

        return self.__scrape(job, response, soup), self.__next_jobs(job, response, soup)
