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

from queue import Queue, Empty
from persistqueue import SQLiteQueue
from shutil import rmtree
from threading import Lock

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
        with self.crawler.state.task():
            cancel_event = self.crawler.cancel_event

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
                    pool_manager=self.crawler.pool_manager,
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

    persistent: bool
    state: CrawlerState
    started: bool
    singular: bool
    __spiders: Dict[str, Spider[CrawlJobDataTypes, CrawlJobOutputDataTypes]]

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

        self.persistent = queue_path is not None
        self.state = CrawlerState()
        self.started = False

        # Memory queue
        if not self.persistent:
            queue = Queue()

        # Persistent queue
        else:
            queue = SQLiteQueue(queue_path, multithreading=True, auto_commit=False)

        self.queue = cast("Queue[CrawlJob[CrawlJobDataTypes]]", queue)

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

        if self.started:
            raise RuntimeError("Crawler already started")

        # Collecting start jobs - we only add those if queue is not pre-existing
        if self.queue.qsize() == 0:

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
            raise RuntimeError("Cannot stop a crawler that has not yet started")

        self.started = False

        if self.persistent and self.queue.qsize() == 0:
            assert self.queue_path is not None
            del self.queue
            rmtree(self.queue_path, ignore_errors=True)

    def __enter__(self):
        super().__enter__()
        self.start()

        return self

    def __exit__(self, *exc):
        self.stop()
        return super().__exit__(*exc)

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

        return safe_wrapper()

    def enqueue(
        self,
        job_or_jobs: Union[
            UrlOrCrawlJob[CrawlJobDataTypes], Iterable[UrlOrCrawlJob[CrawlJobDataType]]
        ],
        spider: Optional[str] = None,
        depth: int = 0,
    ) -> int:
        with self.lock:
            count = 0

            if isinstance(job_or_jobs, (str, CrawlJob)):
                jobs = [job_or_jobs]
            else:
                jobs = job_or_jobs

            jobs = cast(Iterable[UrlOrCrawlJob[CrawlJobDataTypes]], jobs)

            for job in jobs:
                job = ensure_job(job)

                if spider is not None and job.spider is None:
                    job.spider = spider

                if job.depth is None:
                    job.depth = depth

                count += 1
                self.queue.put(job)
                self.state.inc_queued()

            return count

    # NOTE: this is clearly not threadsafe lol. This is for debug only.
    def dump_queue(self):
        jobs = []

        while True:
            try:
                jobs.append(self.queue.get_nowait())
            except Empty:
                break

        for job in jobs:
            self.queue.put_nowait(job)

        return jobs

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
