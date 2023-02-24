# =============================================================================
# Minet Crawler
# =============================================================================
#
# Crawler class invoking multiple spiders to scrape data from the web.
#
from typing import (
    cast,
    Optional,
    TypeVar,
    Callable,
    Dict,
    Iterable,
    Generic,
    Mapping,
)

from queue import Queue
from persistqueue import SQLiteQueue
from shutil import rmtree

from minet.crawl.types import (
    CrawlJob,
    UrlOrCrawlJob,
    CrawlJobDataType,
    ScrapedDataType,
    CrawlResult,
)
from minet.crawl.spiders import Spider, FunctionSpider, DefinitionSpider
from minet.crawl.state import CrawlerState
from minet.scrape.utils import load_definition
from minet.web import request, EXPECTED_WEB_ERRORS
from minet.fetch import HTTPThreadPoolExecutor
from minet.exceptions import UnknownSpiderError, SpiderError
from minet.constants import (
    DEFAULT_DOMAIN_PARALLELISM,
    DEFAULT_IMAP_BUFFER_SIZE,
    DEFAULT_THROTTLE,
    DEFAULT_FETCH_MAX_REDIRECTS,
)


def ensure_job(
    url_or_job: UrlOrCrawlJob[CrawlJobDataType],
) -> CrawlJob[CrawlJobDataType]:
    if isinstance(url_or_job, CrawlJob):
        return url_or_job

    return CrawlJob(url=url_or_job)


RequestArgsType = Callable[[CrawlJob[CrawlJobDataType]], Dict]


class CrawlWorker(Generic[CrawlJobDataType, ScrapedDataType]):
    def __init__(
        self,
        crawler: "Crawler",
        *,
        request_args: Optional[RequestArgsType[CrawlJobDataType]] = None,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        callback: Optional[
            Callable[[CrawlResult[CrawlJobDataType, ScrapedDataType]], None]
        ] = None,
    ):
        self.crawler = crawler
        self.request_args = request_args
        self.max_redirects = max_redirects
        self.callback = callback

    def __call__(
        self, job: CrawlJob[CrawlJobDataType]
    ) -> CrawlResult[CrawlJobDataType, ScrapedDataType]:

        # Registering work
        with self.crawler.state.working():
            result = CrawlResult(job)

            spider = self.crawler.spiders.get(job.spider)

            if spider is None:
                result.error = UnknownSpiderError(spider=job.spider)
                return result

            # NOTE: crawl job must have a url
            assert job.url is not None

            # NOTE: request_args must be threadsafe
            kwargs = {}

            if self.request_args is not None:
                kwargs = self.request_args(job)

            try:
                response = request(
                    job.url,
                    pool_manager=self.crawler.pool_manager,
                    max_redirects=self.max_redirects,
                    **kwargs,
                )

            except EXPECTED_WEB_ERRORS as error:
                result.error = error
                return result

            result.response = response

            try:
                scraped, next_jobs = spider(job, response)
                result.scraped = scraped

                if next_jobs is not None:
                    for job in next_jobs:
                        self.crawler.enqueue(job)

            except Exception as error:
                result.error = SpiderError(reason=error)

            return result


CrawlJobDataTypes = TypeVar("CrawlJobDataTypes", bound=Mapping)
ScrapedDataTypes = TypeVar("ScrapedDataTypes")

# TODO: try creating a kwarg type for those
# TODO: Definition vs. spiders should not be done by the class itself -> DefinitionCrawler
class Crawler(
    HTTPThreadPoolExecutor[
        CrawlJob[CrawlJobDataTypes], CrawlResult[CrawlJobDataTypes, ScrapedDataTypes]
    ]
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
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
        throttle: float = DEFAULT_THROTTLE,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # NOTE: crawling could work depth-first if we wanted

        # Imap params
        self.buffer_size = buffer_size
        self.domain_parallelism = domain_parallelism
        self.throttle = throttle

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

    def __cleanup(self) -> None:
        # Releasing queue (needed by persistqueue)
        if self.using_persistent_queue and self.queue_path is not None:
            del self.queue
            rmtree(self.queue_path, ignore_errors=True)

    def __enter__(self):
        super().__enter__()
        self.__start()

        return self

    def __iter__(self):
        worker = CrawlWorker(self)

        def key_by_domain_name(job: CrawlJob) -> Optional[str]:
            return job.domain

        multithreaded_iterator = super().imap_unordered(
            self.queue,
            worker,
            key=key_by_domain_name,
            buffer_size=self.buffer_size,
            parallelism=self.domain_parallelism,
            throttle=self.throttle,
        )

        def safe_wrapper():
            for result in multithreaded_iterator:
                yield result
                self.queue.task_done()

            self.__cleanup()

        return safe_wrapper()

    def enqueue(self, job: UrlOrCrawlJob[CrawlJobDataTypes]) -> None:
        self.queue.put(ensure_job(job))
        self.state.inc_queued()
