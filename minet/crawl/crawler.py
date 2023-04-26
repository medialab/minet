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

from minet.types import AnyFileTarget
from minet.fs import load_definition
from minet.crawl.types import (
    CrawlJob,
    CrawlTarget,
    UrlOrCrawlTarget,
    CrawlJobDataType,
    CrawlResultDataType,
    SuccessfulCrawlResult,
    ErroredCrawlResult,
    AnyCrawlResult,
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
from minet.executors import HTTPThreadPoolExecutor, CANCELLED
from minet.exceptions import UnknownSpiderError, CancelledRequestError
from minet.constants import (
    DEFAULT_DOMAIN_PARALLELISM,
    DEFAULT_IMAP_BUFFER_SIZE,
    DEFAULT_THROTTLE,
    DEFAULT_FETCH_MAX_REDIRECTS,
    DEFAULT_URLLIB3_TIMEOUT,
)

DEFAULT_SPIDER_KEY = "$$DEFAULT_MINET_SPIDER$$"


def coerce_spider(target):
    if isinstance(target, Spider):
        return target

    if callable(target):
        return FunctionSpider(target)

    raise TypeError("expecting a spider or a callable")


def spider_start_iter(spider: Spider) -> Iterable[UrlOrCrawlTarget]:
    if spider.START_URL is not None:
        yield spider.START_URL

    if spider.START_URLS is not None:
        yield from spider.START_URLS

    if spider.START_TARGET is not None:
        yield spider.START_TARGET

    if spider.START_TARGETS is not None:
        yield from spider.START_TARGETS

    start = spider.start()

    if start is not None:
        yield from start


RequestArgsType = Callable[[CrawlJob[CrawlJobDataType]], Dict]


class CrawlWorker(Generic[CrawlJobDataType, CrawlResultDataType]):
    def __init__(
        self,
        crawler: "Crawler",
        *,
        get_args: Optional[RequestArgsType[CrawlJobDataType]] = None,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
    ):
        self.crawler = crawler
        self.cancel_event = self.crawler.executor.cancel_event
        self.local_context = self.crawler.executor.local_context
        self.get_args = get_args

        self.default_kwargs = {
            "pool_manager": crawler.executor.pool_manager,
            "max_redirects": max_redirects,
            "cancel_event": crawler.executor.cancel_event,
        }

    def __call__(
        self, job: CrawlJob[CrawlJobDataType]
    ) -> Union[object, AnyCrawlResult[CrawlJobDataType, CrawlResultDataType]]:

        # Registering work
        with self.crawler.state.task():
            cancel_event = self.cancel_event

            spider = self.crawler.get_spider(job.spider)

            if spider is None:
                return ErroredCrawlResult(job, UnknownSpiderError(spider=job.spider))

            # NOTE: crawl job must have a url and a depth at that point
            assert job.url is not None
            assert job.depth is not None

            kwargs = {}

            if cancel_event.is_set():
                return CANCELLED

            if self.get_args is not None:
                # NOTE: get_args must be threadsafe
                kwargs = self.get_args(job)

            if cancel_event.is_set():
                return CANCELLED

            try:
                retryer = getattr(self.local_context, "retryer", None)
                kwargs.update(self.default_kwargs)

                if retryer is not None:
                    response = retryer(request, job.url, **kwargs)
                else:
                    response = request(job.url, **kwargs)

            except CancelledRequestError:
                return CANCELLED

            except EXPECTED_WEB_ERRORS as error:
                return ErroredCrawlResult(job, error)

            finally:
                job.attempts += 1

            if cancel_event.is_set():
                return CANCELLED

            try:
                spider_result = spider(job, response)

                if spider_result is not None:
                    data, next_jobs = spider_result
                else:
                    data = None
                    next_jobs = None

                if cancel_event.is_set():
                    return CANCELLED

                degree = 0

                if next_jobs is not None:
                    degree = self.crawler.enqueue(
                        next_jobs, spider=job.spider, depth=job.depth + 1
                    )

            except Exception as error:
                return ErroredCrawlResult(job, error, response=response)

            return SuccessfulCrawlResult(job, response, data, degree)


CrawlJobDataTypes = TypeVar("CrawlJobDataTypes", bound=Mapping)
CrawlResultDataTypes = TypeVar("CrawlResultDataTypes")
Spiders = Union[
    FunctionSpiderCallable[CrawlJobDataTypes, CrawlResultDataTypes],
    Spider[CrawlJobDataTypes, CrawlResultDataTypes],
    Dict[str, Spider[CrawlJobDataTypes, CrawlResultDataTypes]],
]

# TODO: try creating a kwarg type for those
# NOTE: crawling could work depth-first if we wanted
class Crawler(Generic[CrawlJobDataTypes, CrawlResultDataTypes]):
    executor: HTTPThreadPoolExecutor
    queue: CrawlerQueue[CrawlJob[CrawlJobDataTypes]]
    persistent: bool
    state: CrawlerState
    started: bool
    stopped: bool
    resuming: bool
    finished: bool
    singular: bool

    __spiders: Dict[str, Spider[CrawlJobDataTypes, CrawlResultDataTypes]]

    def __init__(
        self,
        spider_or_spiders: Spiders[CrawlJobDataTypes, CrawlResultDataTypes],
        queue_path: Optional[str] = None,
        resume: bool = False,
        dfs: bool = False,
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
        throttle: float = DEFAULT_THROTTLE,
        max_workers: Optional[int] = None,
        wait: bool = True,
        daemonic: bool = False,
        insecure: bool = False,
        timeout: AnyTimeout = DEFAULT_URLLIB3_TIMEOUT,
        spoof_tls_ciphers: bool = False,
        proxy: Optional[str] = None,
        retry: bool = False,
        retryer_kwargs: Optional[Dict[str, Any]] = None,
        get_args: Optional[RequestArgsType[CrawlJobDataType]] = None,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
    ):

        # Own executor and imap params
        self.executor = HTTPThreadPoolExecutor(
            max_workers=max_workers,
            insecure=insecure,
            timeout=timeout,
            wait=wait,
            daemonic=daemonic,
            spoof_tls_ciphers=spoof_tls_ciphers,
            proxy=proxy,
            retry=retry,
            retryer_kwargs=retryer_kwargs,
        )

        self.imap_kwargs = {
            "buffer_size": buffer_size,
            "parallelism": domain_parallelism,
            "throttle": throttle,
        }

        self.worker_kwargs = {"get_args": get_args, "max_redirects": max_redirects}

        # Params
        self.queue_path = queue_path
        self.persistent = queue_path is not None

        # Lifecycle
        self.started = False
        self.stopped = False
        self.resuming = False
        self.finished = False

        # Queue
        self.queue = CrawlerQueue(
            queue_path, resume=resume, cleanup_interval=2, dfs=dfs
        )
        self.persistent = self.queue.persistent
        self.resuming = self.queue.resuming

        if self.resuming and self.queue.qsize() == 0:
            self.finished = True

        # Initializing state
        self.state = CrawlerState(jobs_queued=self.queue.qsize())

        # Spiders
        if isinstance(spider_or_spiders, Mapping):
            self.__spiders = {}
            self.singular = False

            for name, spider in spider_or_spiders.items():
                self.__spiders[name] = coerce_spider(spider)
        elif isinstance(spider_or_spiders, Spider) or callable(spider_or_spiders):
            self.__spiders = {DEFAULT_SPIDER_KEY: coerce_spider(spider_or_spiders)}
            self.singular = True
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

        # Enqueuing start jobs, only if we are not resuming
        if not self.resuming:

            # NOTE: start jobs are all buffered into memory
            # We could use a blocking queue with max size but this could prove
            # difficult to resume crawls based upon lazy iterators
            for name, spider in self.__spiders.items():

                if self.singular:
                    name = None

                self.enqueue(spider_start_iter(spider), spider=name)

        self.started = True

    def stop(self):
        self.stopped = True
        self.executor.shutdown(wait=self.executor.wait)
        del self.queue

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()

    def __iter__(
        self,
    ) -> Iterator[AnyCrawlResult[CrawlJobDataTypes, CrawlResultDataTypes]]:
        worker = CrawlWorker(self, **self.worker_kwargs)

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

            # If iterator ended properly we cleanup the queue
            self.queue.cleanup()

        return safe_wrapper()

    def enqueue(
        self,
        target_or_targets: Union[
            UrlOrCrawlTarget[CrawlJobDataTypes],
            Iterable[UrlOrCrawlTarget[CrawlJobDataTypes]],
        ],
        spider: Optional[str] = None,
        depth: Optional[int] = None,
    ) -> int:
        if isinstance(target_or_targets, (str, CrawlTarget)):
            targets = [target_or_targets]
        else:
            targets = target_or_targets

        def jobs():
            for target in targets:
                if isinstance(target, str):
                    job = CrawlJob(url=target)
                else:
                    job = CrawlJob(
                        url=target.url,
                        depth=target.depth,
                        spider=target.spider,
                        data=target.data,
                    )

                if spider is not None and job.spider is None:
                    job.spider = spider

                if depth is not None:
                    job.depth = depth

                yield job

        count = self.queue.put_many(jobs())

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
        start: Optional[Iterable[UrlOrCrawlTarget]] = None,
        **kwargs,
    ):
        return cls(FunctionSpider(fn, start=start), **kwargs)

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
