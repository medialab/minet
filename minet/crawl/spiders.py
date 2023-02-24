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
from typing_extensions import TypedDict, NotRequired

from urllib.parse import urljoin

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


class DefinitionSpiderCrawlJobOutputDataType(
    TypedDict, Generic[CrawlJobOutputDataType]
):
    single: Optional[CrawlJobOutputDataType]
    multiple: Dict[str, CrawlJobOutputDataType]


class DefinitionSpiderTarget(TypedDict, Generic[CrawlJobDataType]):
    url: str
    spider: NotRequired[str]
    data: NotRequired[CrawlJobDataType]


class DefinitionSpider(
    Spider[
        CrawlJobDataType, DefinitionSpiderCrawlJobOutputDataType[CrawlJobOutputDataType]
    ]
):
    definition: Dict[str, Any]
    next_definition: Optional[Dict[str, Any]]
    max_level: int
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
        self.max_level = definition.get("max_level", float("inf"))

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
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> DefinitionSpiderCrawlJobOutputDataType[CrawlJobOutputDataType]:
        scraped: DefinitionSpiderCrawlJobOutputDataType[CrawlJobOutputDataType] = {
            "single": None,
            "multiple": {},
        }

        context = {"job": job.id(), "url": job.url}

        text = response.text()

        if self.scraper is not None:
            scraped["single"] = self.scraper(text, context=context)

        for name, scraper in self.scrapers.items():
            scraped["multiple"][name] = scraper(text, context=context)

        return scraped

    def __job_from_target(
        self,
        current_url: str,
        target: Union[str, DefinitionSpiderTarget[CrawlJobDataType]],
        next_level: int,
    ) -> CrawlJob[CrawlJobDataType]:
        if isinstance(target, str):
            return CrawlJob(url=urljoin(current_url, target), level=next_level)

        else:

            # TODO: validate target
            return CrawlJob(
                url=urljoin(current_url, target["url"]),
                spider=target.get("spider"),
                level=next_level,
                data=target.get("data"),
            )

    def __next_targets(
        self, response: Response, next_level: int
    ) -> Iterator[Union[str, DefinitionSpiderTarget[CrawlJobDataType]]]:

        text = response.text()

        # Scraping next results
        if self.next_scraper is not None:
            scraped = self.next_scraper(text)

            if scraped is not None:
                if isinstance(scraped, list):
                    yield from scraped
                else:
                    yield scraped

        if self.next_scrapers:
            for scraper in self.next_scrapers.values():
                scraped = scraper(text)

                if scraped is not None:
                    if isinstance(scraped, list):
                        yield from scraped
                    else:
                        yield scraped

        # Formatting next url
        if self.next_definition is not None and "format" in self.next_definition:
            yield FORMATTER.format(self.next_definition["format"], level=next_level)

    def __next_jobs(self, job: CrawlJob[CrawlJobDataType], response: Response):
        if not self.next_definition:
            return

        next_level = job.level + 1

        if next_level > self.max_level:
            return

        for target in self.__next_targets(response, next_level):
            yield self.__job_from_target(response.url, target, next_level)

    def __call__(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> SpiderResult[
        DefinitionSpiderCrawlJobOutputDataType[CrawlJobOutputDataType], CrawlJobDataType
    ]:
        return self.__scrape(job, response), self.__next_jobs(job, response)
