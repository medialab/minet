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
    Tuple,
    Any,
    Generic,
    Mapping,
    Iterable,
    Iterator,
    Union,
)

from threading import Event
from urllib3 import PoolManager

from minet.types import AnyFileTarget
from minet.fs import load_definition
from minet.crawl.types import (
    CrawlJob,
    UrlOrCrawlJob,
    CrawlJobDataType,
    CrawlJobOutputDataType,
    CrawlResult,
)
from minet.crawl.spiders import (
    Spider,
    FunctionSpider,
    FunctionSpiderCallable,
    DefinitionSpider,
)
from minet.crawl.queue import CrawlerQueue, DumpType
from minet.crawl.state import CrawlerState
from minet.web import request, EXPECTED_WEB_ERRORS, AnyTimeout
from minet.fetch import HTTPThreadPoolExecutor, CANCELLED
from minet.exceptions import UnknownSpiderError, CancelledRequestError
from minet.constants import (
    DEFAULT_DOMAIN_PARALLELISM,
    DEFAULT_IMAP_BUFFER_SIZE,
    DEFAULT_THROTTLE,
    DEFAULT_FETCH_MAX_REDIRECTS,
    DEFAULT_URLLIB3_TIMEOUT,
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

    @property
    def cancel_event(self) -> Event:
        return self.crawler.executor.cancel_event

    @property
    def pool_manager(self) -> PoolManager:
        return self.crawler.executor.pool_manager

    def __call__(
        self, job: CrawlJob[CrawlJobDataType]
    ) -> Union[object, CrawlResult[CrawlJobDataType, CrawlJobOutputDataType]]:

        # Registering work
        with self.crawler.state.task():
            cancel_event = self.cancel_event

            result = CrawlResult(job)
            spider = self.crawler.get_spider(job.spider)

            if spider is None:
                result.error = UnknownSpiderError(spider=job.spider)
                return result

            # NOTE: crawl job must have a url and a depth at that point
            assert job.url is not None
            assert job.depth is not None

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
                    pool_manager=self.pool_manager,
                    max_redirects=self.max_redirects,
                    cancel_event=cancel_event,
                    **kwargs,
                )

            except CancelledRequestError:
                return CANCELLED

            except EXPECTED_WEB_ERRORS as error:
                result.error = error
                return result

            finally:
                job.attempts += 1

            result.response = response

            if cancel_event.is_set():
                return CANCELLED

            try:
                output, next_jobs = spider(job, response)
                result.output = output

                if cancel_event.is_set():
                    return CANCELLED

                if next_jobs is not None:
                    result.degree = self.crawler.enqueue(
                        next_jobs, spider=job.spider, depth=job.depth + 1
                    )

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
# NOTE: crawling could work depth-first if we wanted
class Crawler(Generic[CrawlJobDataTypes, CrawlJobOutputDataTypes]):
    executor: HTTPThreadPoolExecutor[
        CrawlJob[CrawlJobDataTypes],
        CrawlResult[CrawlJobDataTypes, CrawlJobOutputDataTypes],
    ]
    queue: CrawlerQueue[CrawlJob[CrawlJobDataTypes]]
    persistent: bool
    state: CrawlerState
    started: bool
    stopped: bool
    resuming: bool
    finished: bool
    singular: bool

    __spiders: Dict[str, Spider[CrawlJobDataTypes, CrawlJobOutputDataTypes]]

    def __init__(
        self,
        spiders: Spiders[CrawlJobDataTypes, CrawlJobOutputDataTypes],
        queue_path: Optional[str] = None,
        resume: bool = False,
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
        throttle: float = DEFAULT_THROTTLE,
        max_workers: Optional[int] = None,
        insecure: bool = False,
        timeout: AnyTimeout = DEFAULT_URLLIB3_TIMEOUT,
        wait: bool = True,
        daemonic: bool = False,
    ):

        # Own executor and imap params
        self.executor = HTTPThreadPoolExecutor(
            max_workers=max_workers,
            insecure=insecure,
            timeout=timeout,
            wait=wait,
            daemonic=daemonic,
        )

        self.imap_kwargs = {
            "buffer_size": buffer_size,
            "parallelism": domain_parallelism,
            "throttle": throttle,
        }

        # Params
        self.queue_path = queue_path
        self.persistent = queue_path is not None

        # Lifecycle
        self.started = False
        self.stopped = False
        self.resuming = False
        self.finished = False

        # Queue
        self.queue = CrawlerQueue(queue_path, resume=resume)
        self.persistent = self.queue.persistent
        self.resuming = self.queue.resuming

        if self.resuming and self.queue.qsize() == 0:
            self.finished = True

        # Initializing state
        self.state = CrawlerState(jobs_queued=self.queue.qsize())

        # Spiders
        if isinstance(spiders, Spider):
            self.__spiders = {DEFAULT_SPIDER_KEY: spiders}
            self.singular = True
        elif isinstance(spiders, Mapping):
            self.__spiders = {}
            self.singular = False

            for name, spider in spiders.items():
                self.__spiders[name] = spider
        else:
            raise TypeError("expecting a single spider or a mapping of spiders")

    def __repr__(self):
        class_name = self.__class__.__name__

        return "<{class_name} {number}>".format(
            class_name=class_name, number="singular" if self.singular else "plural"
        )

    @property
    def plural(self) -> bool:
        return not self.singular

    def get_spider(self, name: Optional[str] = None) -> Spider:
        if name is None and self.plural:
            raise TypeError("plural crawler cannot return default spider")

        if name is not None and self.singular:
            raise TypeError("singular crawler cannot return a spider by name")

        if name is None:
            name = DEFAULT_SPIDER_KEY

        return self.__spiders[name]

    def spiders(self) -> Iterator[Tuple[str, Spider]]:
        if self.singular:
            raise TypeError(
                "singular crawler cannot iterate over its spiders (it only has the default one, use #.get_spider to get it)"
            )

        for name, spiders in self.__spiders.items():
            yield name, spiders

    def start(self) -> None:
        # TODO: maybe start the executor ourselves if required when quenouille moves

        if self.stopped:
            # TODO: we could but we need to mind the condition below
            raise RuntimeError("Cannot restart a crawler")

        if self.finished:
            raise RuntimeError("Cannot start an already finished crawler")

        if self.started:
            raise RuntimeError("Crawler has already started")

        # Collecting start jobs - we only add those if we are not resuming
        if not self.resuming:

            # NOTE: start jobs are all buffered into memory
            # We could use a blocking queue with max size but this could prove
            # difficult to resume crawls based upon lazy iterators
            for name, spider in self.__spiders.items():
                spider_start_jobs = spider.start_jobs()

                if self.singular:
                    name = None

                if spider_start_jobs is not None:
                    self.enqueue(spider_start_jobs, spider=name)

        self.started = True

    def stop(self):
        if not self.started:
            raise TypeError("Crawler has not started yet")

        self.stopped = True
        self.executor.shutdown(wait=self.executor.wait)
        del self.queue

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()

    def __iter__(self):
        worker = CrawlWorker(self)

        def key_by_domain_name(job: CrawlJob) -> Optional[str]:
            return job.domain

        imap_unordered = self.executor.imap_unordered(
            self.queue, worker, key=key_by_domain_name, **self.imap_kwargs
        )

        def safe_wrapper():
            for result in imap_unordered:
                if result is CANCELLED:
                    continue

                yield result

                self.queue.ack(result.job)

        return safe_wrapper()

    def enqueue(
        self,
        job_or_jobs: Union[
            UrlOrCrawlJob[CrawlJobDataTypes], Iterable[UrlOrCrawlJob[CrawlJobDataTypes]]
        ],
        spider: Optional[str] = None,
        depth: int = 0,
    ) -> int:
        if isinstance(job_or_jobs, (str, CrawlJob)):
            jobs = [job_or_jobs]
        else:
            jobs = job_or_jobs

        def proper_jobs():
            for job in jobs:
                job = ensure_job(job)

                if spider is not None and job.spider is None:
                    job.spider = spider

                if job.depth is None:
                    job.depth = depth

                yield job

        count = self.queue.put_many(proper_jobs())

        self.state.inc_queued(count)

        return count

    # NOTE: this is clearly not threadsafe lol. This is for debug only.
    def dump_queue(self) -> DumpType[CrawlJob[CrawlJobDataTypes]]:
        if self.started:
            raise TypeError("cannot dump queue while crawler is running")

        return self.queue.dump()

    @classmethod
    def from_callable(
        cls,
        fn: FunctionSpiderCallable,
        start_jobs: Optional[Iterable[UrlOrCrawlJob]] = None,
        **kwargs,
    ):
        return cls(FunctionSpider(fn, start_jobs=start_jobs), **kwargs)

    @classmethod
    def from_definition(
        cls, definition: Union[Dict[str, Any], AnyFileTarget], **kwargs
    ):
        if not isinstance(definition, dict):
            definition = load_definition(definition)

        definition = cast(Dict[str, Any], definition)

        # Do we have a single spider or multiple spiders?
        if "spiders" in definition:
            spiders = {
                name: DefinitionSpider(s) for name, s in definition["spiders"].items()
            }
        else:
            spiders = DefinitionSpider(definition)

        return cls(spiders, **kwargs)
