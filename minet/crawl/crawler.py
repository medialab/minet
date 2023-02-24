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
    Generic,
    Mapping,
    Iterable,
    Union,
)

from queue import Queue
from persistqueue import SQLiteQueue
from shutil import rmtree
from threading import Lock

from minet.crawl.types import (
    CrawlJob,
    UrlOrCrawlJob,
    CrawlJobDataType,
    CrawlJobOutputDataType,
    CrawlResult,
)
from minet.crawl.spiders import Spider
from minet.crawl.state import CrawlerState
from minet.web import request, EXPECTED_WEB_ERRORS
from minet.fetch import HTTPThreadPoolExecutor, CANCELLED
from minet.exceptions import UnknownSpiderError, CancelledRequestError
from minet.constants import (
    DEFAULT_DOMAIN_PARALLELISM,
    DEFAULT_IMAP_BUFFER_SIZE,
    DEFAULT_THROTTLE,
    DEFAULT_FETCH_MAX_REDIRECTS,
)

DEFAULT_SPIDER_KEY = "$$DEFAULT_MINET_SPIDER$$"


def ensure_job(
    url_or_job: UrlOrCrawlJob[CrawlJobDataType],
) -> CrawlJob[CrawlJobDataType]:
    if isinstance(url_or_job, CrawlJob):
        return url_or_job

    return CrawlJob(url=url_or_job)


RequestArgsType = Callable[[CrawlJob[CrawlJobDataType]], Dict]


class CrawlWorker(Generic[CrawlJobDataType, CrawlJobOutputDataType]):
    def __init__(
        self,
        crawler: "Crawler",
        *,
        request_args: Optional[RequestArgsType[CrawlJobDataType]] = None,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        callback: Optional[
            Callable[[CrawlResult[CrawlJobDataType, CrawlJobOutputDataType]], None]
        ] = None,
    ):
        self.crawler = crawler
        self.request_args = request_args
        self.max_redirects = max_redirects
        self.callback = callback

    def __call__(
        self, job: CrawlJob[CrawlJobDataType]
    ) -> Union[object, CrawlResult[CrawlJobDataType, CrawlJobOutputDataType]]:

        # Registering work
        with self.crawler.state.working():
            cancel_event = self.crawler.cancel_event

            result = CrawlResult(job)
            spider_name = job.spider or DEFAULT_SPIDER_KEY

            spider = self.crawler.spiders.get(spider_name)

            if spider is None:
                result.error = UnknownSpiderError(spider=job.spider)
                return result

            # NOTE: crawl job must have a url
            assert job.url is not None

            # NOTE: request_args must be threadsafe
            kwargs = {}

            if cancel_event.is_set():
                return CANCELLED

            if self.request_args is not None:
                kwargs = self.request_args(job)

            if cancel_event.is_set():
                return CANCELLED

            try:
                response = request(
                    job.url,
                    pool_manager=self.crawler.pool_manager,
                    max_redirects=self.max_redirects,
                    **kwargs,
                )

            except CancelledRequestError:
                return CANCELLED

            except EXPECTED_WEB_ERRORS as error:
                result.error = error
                return result

            result.response = response

            if cancel_event.is_set():
                return CANCELLED

            try:
                output, next_jobs = spider(job, response)
                result.output = output

                if cancel_event.is_set():
                    return CANCELLED

                if next_jobs is not None:
                    self.crawler.enqueue_many(next_jobs, spider=spider_name)

            except Exception as error:
                result.error = error

            return result


CrawlJobDataTypes = TypeVar("CrawlJobDataTypes", bound=Mapping)
CrawlJobOutputDataTypes = TypeVar("CrawlJobOutputDataTypes")
Spiders = Union[
    Spider[CrawlJobDataTypes, CrawlJobOutputDataTypes],
    Dict[str, Spider[CrawlJobDataTypes, CrawlJobOutputDataTypes]],
]

# TODO: try creating a kwarg type for those
class Crawler(
    HTTPThreadPoolExecutor[
        CrawlJob[CrawlJobDataTypes],
        CrawlResult[CrawlJobDataTypes, CrawlJobOutputDataTypes],
    ]
):
    buffer_size: int
    domain_parallelism: int
    throttle: float

    queue: "Queue[CrawlJob[CrawlJobDataTypes]]"
    lock: Lock

    using_persistent_queue: bool
    state: CrawlerState
    started: bool
    spiders: Dict[str, Spider[CrawlJobDataTypes, CrawlJobOutputDataTypes]]

    def __init__(
        self,
        spiders: Spiders[CrawlJobDataTypes, CrawlJobOutputDataTypes],
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
        self.lock = Lock()

        # Params
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

        self.queue = cast("Queue[CrawlJob[CrawlJobDataTypes]]", queue)

        # Spiders
        if isinstance(spiders, Spider):
            self.spiders = {DEFAULT_SPIDER_KEY: spiders}
        elif isinstance(spiders, Mapping):
            self.spiders = {}

            for name, spider in spiders.items():
                self.spiders[name] = spider
        else:
            raise TypeError("expecting a single spider or a mapping of spiders")

    def __start(self):

        if self.started:
            raise RuntimeError("already started")

        # Collecting start jobs - we only add those if queue is not pre-existing
        if self.queue.qsize() == 0:

            # NOTE: start jobs are all buffered into memory
            # We could use a blocking queue with max size but this could prove
            # difficult to resume crawls based upon lazy iterators
            if self.spiders is not None:
                for name, spider in self.spiders.items():
                    spider_start_jobs = spider.start_jobs()

                    if spider_start_jobs is not None:
                        self.enqueue_many(spider_start_jobs, spider=name)

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

        imap_unordered = super().imap_unordered(
            self.queue,
            worker,
            key=key_by_domain_name,
            buffer_size=self.buffer_size,
            parallelism=self.domain_parallelism,
            throttle=self.throttle,
        )

        def safe_wrapper():
            for result in imap_unordered:
                if result is CANCELLED:
                    continue

                yield result
                self.queue.task_done()

            self.__cleanup()

        return safe_wrapper()

    def enqueue(
        self, job: UrlOrCrawlJob[CrawlJobDataTypes], spider: Optional[str] = None
    ) -> None:
        with self.lock:
            job = ensure_job(job)

            if spider is not None and job.spider is None:
                job.spider = spider

            self.queue.put(job)
            self.state.inc_queued()

    def enqueue_many(
        self,
        jobs: Iterable[UrlOrCrawlJob[CrawlJobDataTypes]],
        spider: Optional[str] = None,
    ) -> None:
        with self.lock:
            for job in jobs:
                job = ensure_job(job)

                if spider is not None and job.spider is None:
                    job.spider = spider

                self.queue.put(job)
                self.state.inc_queued()


# NOTE: code below to create crawler from definition file

# Creating spiders
# if spec is not None:
#     if not isinstance(spec, dict):
#         spec = load_definition(spec)

#     if "spiders" in spec:
#         spiders = {
#             name: DefinitionSpider(s, name=name)
#             for name, s in spec["spiders"].items()
#         }  # type: ignore
#         self.single_spider = False
#     else:
#         spiders = {"default": DefinitionSpider(spec)}  # type: ignore
#         self.single_spider = True

# elif spider is not None:
#     spiders = {"default": spider}

# elif spiders is None:
#     raise TypeError(
#         "minet.Crawler: expecting either `spec`, `spider` or `spiders`."
#     )
