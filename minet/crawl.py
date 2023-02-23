# =============================================================================
# Minet Crawl
# =============================================================================
#
# Functions related to the crawling utilities of minet.
#
from dataclasses import dataclass
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
    Mapping,
)
from typing_extensions import TypedDict, NotRequired

import urllib3
from queue import Queue
from persistqueue import SQLiteQueue
from quenouille import imap_unordered
from ural import get_domain_name
from urllib.parse import urljoin
from shutil import rmtree
from threading import Lock

from minet.scrape import Scraper
from minet.scrape.utils import load_definition
from minet.web import (
    create_pool_manager,
    request,
    Response,
    AnyTimeout,
    EXPECTED_WEB_ERRORS,
)
from minet.fetch import HTTPThreadPoolExecutor
from minet.utils import PseudoFStringFormatter

from minet.exceptions import UnknownSpiderError

from minet.constants import (
    DEFAULT_DOMAIN_PARALLELISM,
    DEFAULT_IMAP_BUFFER_SIZE,
    DEFAULT_THROTTLE,
    DEFAULT_URLLIB3_TIMEOUT,
    DEFAULT_FETCH_MAX_REDIRECTS,
)

FORMATTER = PseudoFStringFormatter()

T = TypeVar("T")
CrawlJobDataType = TypeVar("CrawlJobDataType", bound=Mapping)
ScrapedDataType = TypeVar("ScrapedDataType")


def ensure_list(value: Union[T, List[T]]) -> List[T]:
    if not isinstance(value, list):
        return [value]
    return value


class CrawlJob(Generic[CrawlJobDataType]):
    __slots__ = ("url", "level", "spider", "data", "__has_cached_domain", "__domain")

    url: str
    level: int
    spider: str
    data: Optional[CrawlJobDataType]

    __has_cached_domain: bool
    __domain: Optional[str]

    def __init__(
        self,
        url: str,
        level: int = 0,
        spider: str = "default",
        data: Optional[CrawlJobDataType] = None,
    ):
        self.url = url
        self.level = level
        self.spider = spider
        self.data = data

    def id(self) -> str:
        return "%x" % id(self)

    @property
    def domain(self) -> Optional[str]:
        if self.__has_cached_domain:
            return self.__domain

        if self.url is not None:
            self.__domain = get_domain_name(self.url)

        self.__has_cached_domain = True

        return self.__domain

    def __repr__(self):
        class_name = self.__class__.__name__

        return ("<%(class_name)s level=%(level)s url=%(url)s spider=%(spider)s>") % {
            "class_name": class_name,
            "url": self.url,
            "level": self.level,
            "spider": self.spider,
        }


UrlOrCrawlJob = Union[str, CrawlJob[CrawlJobDataType]]


def crawl_job_grouper(job: CrawlJob):
    return get_domain_name(job.url)


def ensure_job(
    url_or_job: UrlOrCrawlJob[CrawlJobDataType],
) -> CrawlJob[CrawlJobDataType]:
    if isinstance(url_or_job, CrawlJob):
        return url_or_job

    return CrawlJob(url=url_or_job)


class CrawlerState(object):
    jobs_done: int
    jobs_doing: int
    jobs_queued: int
    __lock: Lock

    def __init__(self):
        self.__lock = Lock()

        self.jobs_done = 0
        self.jobs_doing = 0
        self.jobs_queued = 0

    def inc_queued(self) -> None:
        with self.__lock:
            self.jobs_queued += 1

    def dec_queued(self) -> None:
        with self.__lock:
            self.jobs_queued -= 1

    def inc_done(self) -> None:
        with self.__lock:
            self.jobs_done += 1

    def inc_doing(self) -> None:
        with self.__lock:
            self.jobs_doing += 1

    def dec_doing(self) -> None:
        with self.__lock:
            self.jobs_doing -= 1

    def inc_working(self) -> None:
        with self.__lock:
            self.jobs_queued -= 1
            self.jobs_doing += 1

    def dec_working(self) -> None:
        with self.__lock:
            self.jobs_done += 1
            self.jobs_doing -= 1

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            "<%(class_name)s queued=%(jobs_queued)i doing=%(jobs_doing)i done=%(jobs_done)i>"
        ) % {
            "class_name": class_name,
            "jobs_done": self.jobs_done,
            "jobs_queued": self.jobs_queued,
            "jobs_doing": self.jobs_doing,
        }


SpiderNextJobs = Optional[Iterable[CrawlJob[CrawlJobDataType]]]
SpiderResult = Tuple[ScrapedDataType, SpiderNextJobs[CrawlJobDataType]]


class Spider(Generic[CrawlJobDataType, ScrapedDataType]):
    name: str

    def __init__(self, name: str = "default"):
        self.name = name

    def start_jobs(self) -> Optional[Iterable[UrlOrCrawlJob[CrawlJobDataType]]]:
        return None

    def __call__(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> SpiderResult[ScrapedDataType, CrawlJobDataType]:
        raise NotImplementedError

    def __repr__(self):
        class_name = self.__class__.__name__

        return "<%(class_name)s name=%(name)s>" % {
            "class_name": class_name,
            "name": self.name,
        }


class FunctionSpider(Spider[CrawlJobDataType, ScrapedDataType]):
    fn: Callable[
        [CrawlJob[CrawlJobDataType], Response],
        SpiderResult[ScrapedDataType, CrawlJobDataType],
    ]

    def __init__(
        self,
        fn: Callable[
            [CrawlJob[CrawlJobDataType], Response],
            SpiderResult[ScrapedDataType, CrawlJobDataType],
        ],
        name: str = "default",
    ):
        super().__init__(name)
        self.fn = fn

    def __call__(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> SpiderResult[ScrapedDataType, CrawlJobDataType]:
        return self.fn(job, response)


class DefinitionSpiderScrapedDataType(TypedDict, Generic[ScrapedDataType]):
    single: Optional[ScrapedDataType]
    multiple: Dict[str, ScrapedDataType]


class DefinitionSpiderTarget(TypedDict, Generic[CrawlJobDataType]):
    url: str
    spider: NotRequired[str]
    data: NotRequired[CrawlJobDataType]


class DefinitionSpider(
    Spider[CrawlJobDataType, DefinitionSpiderScrapedDataType[ScrapedDataType]]
):
    definition: Dict[str, Any]
    next_definition: Optional[Dict[str, Any]]
    max_level: int
    scraper: Optional[Scraper]
    scrapers: Dict[str, Scraper]
    next_scraper: Optional[Scraper]
    next_scrapers: Dict[str, Scraper]

    def __init__(self, definition: Dict[str, Any], name: str = "default"):

        # Descriptors
        super().__init__(name)
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

        # TODO: possibility to name this as jobs
        start_urls = ensure_list(self.definition.get("start_url", [])) + ensure_list(
            self.definition.get("start_urls", [])
        )

        for url in start_urls:
            yield CrawlJob(url, spider=self.name)

    def __scrape(
        self, job: CrawlJob[CrawlJobDataType], response: Response
    ) -> DefinitionSpiderScrapedDataType[ScrapedDataType]:
        scraped: DefinitionSpiderScrapedDataType[ScrapedDataType] = {
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
            return CrawlJob(
                url=urljoin(current_url, target), spider=self.name, level=next_level
            )

        else:

            # TODO: validate target
            return CrawlJob(
                url=urljoin(current_url, target["url"]),
                spider=target.get("spider", self.name),
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
        DefinitionSpiderScrapedDataType[ScrapedDataType], CrawlJobDataType
    ]:
        return self.__scrape(job, response), self.__next_jobs(job, response)


ItemType = TypeVar("ItemType")


class CrawlResult(Generic[CrawlJobDataType, ScrapedDataType]):
    __slots__ = ("job", "scraped", "error", "response")

    job: CrawlJob[CrawlJobDataType]
    scraped: Optional[ScrapedDataType]
    error: Optional[Exception]
    response: Optional[Response]
    # next_jobs: Optional[List[CrawlJob[CrawlJobDataType]]]

    def __init__(self, job: CrawlJob[CrawlJobDataType]):
        self.job = job
        self.scraped = None
        self.error = None
        self.response = None
        # self.next_jobs = None

    def __repr__(self):
        name = self.__class__.__name__

        if not self.response:
            return "<{name} url={url!r} pending!>".format(name=name, url=self.job.url)

        if self.error:
            return "<{name} url={url!r} error={error}>".format(
                name=name, url=self.job.url, error=self.error.__class__.__name__
            )

        assert self.response is not None

        return "<{name} url={url!r} status={status!r}>".format(
            name=name, url=self.job.url, status=self.response.status
        )


RequestArgsType = Callable[[CrawlJob[CrawlJobDataType]], Dict]


class CrawlWorker(Generic[CrawlJobDataType, ScrapedDataType]):
    pool_manager: urllib3.PoolManager

    def __init__(
        self,
        pool_manager: urllib3.PoolManager,
        state: CrawlerState,
        queue: "Queue[CrawlJob[CrawlJobDataTypes]]",
        *,
        request_args: Optional[RequestArgsType[CrawlJobDataType]] = None,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        callback: Optional[
            Callable[[CrawlResult[CrawlJobDataType, ScrapedDataType]], None]
        ] = None,
    ):
        self.pool_manager = pool_manager
        self.state = state
        self.queue = queue
        self.request_args = request_args
        self.max_redirects = max_redirects
        self.callback = callback

    def __call__(
        self, job: CrawlJob[CrawlJobDataType]
    ) -> CrawlResult[CrawlJobDataType, ScrapedDataType]:
        result = CrawlResult(job)

        # NOTE: crawl job must have a url
        assert job.url is not None

        # NOTE: request_args must be threadsafe
        kwargs = {}

        if self.request_args is not None:
            kwargs = self.request_args(job)

        try:
            response = request(
                job.url,
                pool_manager=self.pool_manager,
                max_redirects=self.max_redirects,
                **kwargs,
            )

        except EXPECTED_WEB_ERRORS as error:
            result.error = error

        else:
            result.response = response

        # TODO: scrape and acquire next jobs here

        return result


CrawlJobDataTypes = TypeVar("CrawlJobDataTypes", bound=Mapping)
ScrapedDataTypes = TypeVar("ScrapedDataTypes")

# TODO: try creating a kwarg type for those
class Crawler(
    HTTPThreadPoolExecutor[ItemType, CrawlResult[CrawlJobDataTypes, ScrapedDataTypes]]
):
    queue: "Queue[CrawlJob[CrawlJobDataTypes]]"

    def __init__(
        self,
        spec=None,
        spider: Optional[Spider[CrawlJobDataTypes, ScrapedDataTypes]] = None,
        spiders: Optional[
            Dict[str, Spider[CrawlJobDataTypes, ScrapedDataTypes]]
        ] = None,
        start_jobs: Optional[Iterable[UrlOrCrawlJob[CrawlJobDataTypes]]] = None,
        queue_path: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # NOTE: crawling could work depth-first if we wanted

        # Params
        self.start_jobs = start_jobs
        self.queue_path = queue_path

        self.using_persistent_queue = queue_path is not None
        self.state = CrawlerState()
        self.started = False

        # Memory queue
        if not self.using_persistent_queue:
            queue = Queue()

        # Persistent queue
        else:
            queue = SQLiteQueue(queue_path, multithreading=True, auto_commit=False)

        # Creating spiders
        if spec is not None:
            if not isinstance(spec, dict):
                spec = load_definition(spec)

            if "spiders" in spec:
                spiders = {
                    name: DefinitionSpider(s, name=name)
                    for name, s in spec["spiders"].items()
                }  # type: ignore
                self.single_spider = False
            else:
                spiders = {"default": DefinitionSpider(spec)}  # type: ignore
                self.single_spider = True

        elif spider is not None:
            spiders = {"default": spider}

        elif spiders is None:
            raise TypeError(
                "minet.Crawler: expecting either `spec`, `spider` or `spiders`."
            )

        assert spiders is not None

        # Solving function spiders
        for name, s in spiders.items():
            if callable(s) and not isinstance(s, Spider):
                spiders[name] = FunctionSpider(s, name)

        self.queue = cast("Queue", queue)
        self.spiders = spiders

    def __start(self):

        if self.started:
            raise RuntimeError("already started")

        # Collecting start jobs - we only add those if queue is not pre-existing
        if self.queue.qsize() == 0:

            # NOTE: start jobs are all buffered into memory
            # We could use a blocking queue with max size but this could prove
            # difficult to resume crawls based upon lazy iterators
            if self.start_jobs:
                for job in self.start_jobs:
                    self.enqueue(job)

            if self.spiders is not None:
                for spider in self.spiders.values():
                    spider_start_jobs = spider.start_jobs()

                    if spider_start_jobs is not None:
                        for job in spider_start_jobs:
                            self.enqueue(job)

        self.started = True

    def enqueue(self, job: UrlOrCrawlJob[CrawlJobDataTypes]) -> None:
        self.queue.put(ensure_job(job))
        self.state.inc_queued()


class OldCrawler(object):
    def work(self, job):
        self.state.inc_working()

        spider = self.spiders.get(job.spider)

        if spider is None:
            raise UnknownSpiderError('Unknown spider "%s"' % job.spider)

        try:
            response = request(job.url, pool_manager=self.pool_manager)
        except EXPECTED_WEB_ERRORS as err:
            return CrawlWorkerResult(
                job=job,
                scraped=None,
                error=err,
                response=None,
                meta=None,
                content=None,
                next_jobs=None,
            )

        meta = spider.extract_meta_from_response(job, response)

        # Decoding response content
        content = spider.process_content(job, response, meta)

        if isinstance(spider, FunctionSpider):
            scraped, next_jobs = spider.process(job, response, content, meta)
        else:

            # Scraping items
            scraped = spider.scrape(job, response, content, meta)

            # Finding next jobs
            next_jobs = spider.next_jobs(job, response, content, meta)

        # Enqueuing next jobs
        if next_jobs is not None:

            # Consuming so that multiple agents may act on this
            next_jobs = list(next_jobs)
            self.enqueue(next_jobs)

        self.state.dec_working()

        return CrawlWorkerResult(
            job=job,
            scraped=scraped,
            error=None,
            response=response,
            meta=meta,
            content=content,
            next_jobs=next_jobs,
        )

    def __iter__(self):

        self.start()

        multithreaded_iterator = imap_unordered(
            self.queue,
            self.work,
            self.threads,
            key=CrawlJob.grouper,
            parallelism=DEFAULT_DOMAIN_PARALLELISM,
            buffer_size=self.buffer_size,
            throttle=self.throttle,
            wait=self.wait,
            daemonic=self.daemonic,
        )

        def generator():
            for result in multithreaded_iterator:
                yield result
                self.queue.task_done()

            self.cleanup()

        return generator()

    def cleanup(self):

        # Releasing queue (needed by persistqueue)
        if self.using_persistent_queue:
            del self.queue
            rmtree(self.queue_path, ignore_errors=True)
