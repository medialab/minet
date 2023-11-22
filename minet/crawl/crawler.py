# =============================================================================
# Minet Crawler
# =============================================================================
#
# Crawler class invoking multiple spiders to scrape data from the web.
#
from typing import (
    cast,
    overload,
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
from minet.types import ParamSpec

from os import makedirs
from os.path import join
from threading import Lock
from urllib.parse import urljoin
from ural import ensure_protocol, get_domain_name
from multiprocessing import Pool

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
)
from minet.crawl.exceptions import CrawlerAlreadyFinishedError
from minet.crawl.queue import CrawlerQueue, AnyParallelism, AnyThrottle
from minet.crawl.state import CrawlerState
from minet.crawl.url_cache import URLCache
from minet.web import request, EXPECTED_WEB_ERRORS, AnyTimeout
from minet.fs import ThreadSafeFileWriter
from minet.executors import HTTPThreadPoolExecutor, CallbackResultType
from minet.exceptions import UnknownSpiderError, CancelledRequestError
from minet.constants import (
    DEFAULT_DOMAIN_PARALLELISM,
    DEFAULT_THROTTLE,
    DEFAULT_FETCH_MAX_REDIRECTS,
    DEFAULT_URLLIB3_TIMEOUT,
)

P = ParamSpec("P")
T = TypeVar("T")

DEFAULT_SPIDER_KEY = object()


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


class CrawlWorker(Generic[CrawlJobDataType, CrawlResultDataType, CallbackResultType]):
    def __init__(
        self,
        crawler: "Crawler",
        *,
        request_args: Optional[RequestArgsType[CrawlJobDataType]] = None,
        use_pycurl: bool = False,
        compressed: bool = False,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        stateful_redirects: bool = False,
        spoof_ua: bool = False,
        known_encoding: Optional[str] = None,
        callback: Optional[
            Callable[
                [
                    "Crawler",
                    SuccessfulCrawlResult[CrawlJobDataType, CrawlResultDataType],
                ],
                CallbackResultType,
            ]
        ] = None
    ):
        self.crawler = crawler
        self.cancel_event = self.crawler.executor.cancel_event
        self.local_context = self.crawler.executor.local_context
        self.request_args = request_args
        self.max_depth = crawler.max_depth
        self.callback = callback

        self.default_kwargs = {
            "pool_manager": crawler.executor.pool_manager,
            "max_redirects": max_redirects,
            "stateful": stateful_redirects,
            "spoof_ua": spoof_ua,
            "cancel_event": crawler.executor.cancel_event,
        }

        if use_pycurl:
            del self.default_kwargs["pool_manager"]
            self.default_kwargs["use_pycurl"] = True

        if compressed:
            self.default_kwargs["compressed"] = True

        if known_encoding is not None:
            self.default_kwargs["known_encoding"] = known_encoding

    def __call__(
        self, job: CrawlJob[CrawlJobDataType]
    ) -> Optional[
        Tuple[
            AnyCrawlResult[CrawlJobDataType, CrawlResultDataType],
            Optional[CallbackResultType],
        ]
    ]:
        # Registering work
        with self.crawler.state.task(), self.crawler.queue.group_releaser(job):
            cancel_event = self.cancel_event

            spider = self.crawler.get_spider(job.spider)

            if spider is None:
                assert job.spider is not None
                return ErroredCrawlResult(job, UnknownSpiderError(job.spider)), None

            # NOTE: crawl job must have a url and a depth at that point
            assert job.url is not None
            assert job.depth is not None

            kwargs = self.default_kwargs.copy()

            if cancel_event.is_set():
                return

            if self.request_args is not None:
                # NOTE: request_args must be threadsafe
                kwargs.update(self.request_args(job))

            if cancel_event.is_set():
                return

            try:
                retryer = getattr(self.local_context, "retryer", None)

                if retryer is not None:
                    response = retryer(request, job.url, **kwargs)
                else:
                    response = request(job.url, **kwargs)

                # If end url is different from job we add the url to visited cache
                # NOTE: this is somewhat subject to race conditions but it should
                # be benign and still be useful in some cases.
                if self.crawler.url_cache is not None and job.url != response.end_url:
                    with self.crawler.enqueue_lock:
                        self.crawler.url_cache.add(response.end_url)

            except CancelledRequestError:
                return

            except EXPECTED_WEB_ERRORS as error:
                return ErroredCrawlResult(job, error), None

            if cancel_event.is_set():
                return

            spider_result = spider.process(job, response)

            if spider_result is not None:
                data, next_jobs = spider_result
            else:
                data = None
                next_jobs = None

            if cancel_event.is_set():
                return

            degree = 0

            if next_jobs is not None:
                if self.max_depth is None or job.depth < self.max_depth:
                    degree = self.crawler.enqueue(
                        next_jobs,
                        spider=job.spider,
                        depth=job.depth + 1,
                        base_url=response.end_url,
                        parent=job,
                    )

            result = SuccessfulCrawlResult(job, response, data, degree)

            # NOTE: at one point we might want to retry the callback like
            # in the HTTPWorker
            callback_result = None

            if self.callback is not None:
                callback_result = self.callback(self.crawler, result)  # type: ignore

            return result, callback_result  # type: ignore


CrawlJobDataTypes = TypeVar("CrawlJobDataTypes")
CrawlResultDataTypes = TypeVar("CrawlResultDataTypes")
AnySpider = Union[
    FunctionSpiderCallable[CrawlJobDataTypes, CrawlResultDataTypes],
    Spider[CrawlJobDataTypes, CrawlResultDataTypes],
]
SpiderDeclaration = Union[
    AnySpider[CrawlJobDataTypes, CrawlResultDataTypes],
    Dict[str, AnySpider[CrawlJobDataTypes, CrawlResultDataTypes]],
]


# TODO: try creating a kwarg type for those
class Crawler(Generic[CrawlJobDataTypes, CrawlResultDataTypes]):
    executor: HTTPThreadPoolExecutor

    enqueue_lock: Lock

    queue: CrawlerQueue
    persistent: bool

    state: CrawlerState

    started: bool
    stopped: bool
    resuming: bool
    singular: bool

    __spiders: Dict[Union[object, str], Spider[CrawlJobDataTypes, CrawlResultDataTypes]]

    def __init__(
        self,
        spider_or_spiders: SpiderDeclaration[CrawlJobDataTypes, CrawlResultDataTypes],
        persistent_storage_path: Optional[str] = None,
        sqlar: bool = False,
        visit_urls_only_once: bool = False,
        normalized_url_cache: bool = False,
        max_depth: Optional[int] = None,
        resume: bool = False,
        lifo: bool = False,
        writer_root_directory: Optional[str] = None,
        domain_parallelism: AnyParallelism = DEFAULT_DOMAIN_PARALLELISM,
        throttle: AnyThrottle = DEFAULT_THROTTLE,
        process_pool_workers: Optional[int] = None,
        max_workers: Optional[int] = None,
        wait: bool = True,
        daemonic: bool = False,
        insecure: bool = False,
        timeout: AnyTimeout = DEFAULT_URLLIB3_TIMEOUT,
        spoof_tls_ciphers: bool = False,
        proxy: Optional[str] = None,
        retry: bool = False,
        retryer_kwargs: Optional[Dict[str, Any]] = None,
        request_args: Optional[RequestArgsType[CrawlJobDataType]] = None,
        use_pycurl: bool = False,
        compressed: bool = False,
        known_encoding: Optional[str] = None,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        stateful_redirects: bool = False,
        spoof_ua: bool = False,
    ):
        # Validation
        if resume and persistent_storage_path is None:
            raise TypeError("cannot resume a non-persistent crawler")

        # Utilities
        self.file_writer = ThreadSafeFileWriter(writer_root_directory, sqlar=sqlar)
        self.process_pool = None

        # NOTE: if not None and not 0 basically
        if process_pool_workers:
            self.process_pool = Pool(process_pool_workers)

        # Params
        self.persistent_storage_path = persistent_storage_path
        self.persistent = persistent_storage_path is not None
        self.queue_path = None
        self.url_cache_path = None
        self.max_depth = max_depth

        if self.persistent_storage_path is not None:
            makedirs(self.persistent_storage_path, exist_ok=True)

            self.queue_path = join(self.persistent_storage_path, "queue")
            self.url_cache_path = join(self.persistent_storage_path, "urls")

        # Threading
        self.enqueue_lock = Lock()

        # Lifecycle
        self.started = False
        self.stopped = False
        self.resuming = False

        # Queue
        self.queue = CrawlerQueue(
            self.queue_path,
            resume=resume,
            group_parallelism=domain_parallelism,
            throttle=throttle,
            lifo=lifo,
        )
        self.persistent = self.queue.persistent
        self.resuming = (
            self.queue.resuming
        )  # TODO: should probably also check url cache integrity

        if self.resuming and self.queue.qsize() == 0:
            raise CrawlerAlreadyFinishedError

        # Url cache
        self.unique = visit_urls_only_once
        self.url_cache = (
            URLCache(self.url_cache_path, normalized=normalized_url_cache)
            if self.unique
            else None
        )

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

        # Attaching spiders
        for spider in self.__spiders.values():
            spider.attach(self)

        # Own executor and imap params
        # NOTE: the process pool is initialized before the HTTPThreadPoolExecutor
        # so that we don't have potential issues related to urllib3.PoolManager
        # not being fork-safe.
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

        # NOTE: buffer_size=0 is very important to avoid quenouille's optimistic
        # buffer. Remember also that this cannot work if quenouille must handle
        # group parallelism or throttle, which is why it's the crawler queue's
        # job now.
        self.imap_kwargs = {"buffer_size": 0, "panic": self.queue.unblock}

        self.worker_kwargs = {
            "request_args": request_args,
            "max_redirects": max_redirects,
            "stateful_redirects": stateful_redirects,
            "spoof_ua": spoof_ua,
            "use_pycurl": use_pycurl,
            "compressed": compressed,
            "known_encoding": known_encoding,
        }

    def __repr__(self):
        class_name = self.__class__.__name__

        return "<{class_name} {number}>".format(
            class_name=class_name, number="singular" if self.singular else "plural"
        )

    def __len__(self) -> int:
        return self.queue.qsize()

    @property
    def plural(self) -> bool:
        return not self.singular

    def get_spider(self, name: Optional[str] = None) -> Spider:
        if name is None and self.plural:
            raise TypeError("plural crawler cannot return default spider")

        if name is not None and self.singular:
            raise TypeError("singular crawler cannot return a spider by name")

        if name is None:
            name = cast(str, DEFAULT_SPIDER_KEY)

        return self.__spiders[name]

    def spiders(self) -> Iterator[Tuple[str, Spider]]:
        if self.singular:
            raise TypeError(
                "singular crawler cannot iterate over its spiders (it only has the default one, use #.get_spider to get it)"
            )

        for name, spiders in self.__spiders.items():
            assert isinstance(name, str)
            yield name, spiders

    def start(self) -> None:
        # TODO: maybe start the executor ourselves if required when quenouille moves

        if self.stopped:
            # TODO: we could but we need to mind the condition below
            raise RuntimeError("Cannot restart a crawler")

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

                assert name is None or isinstance(name, str)

                self.enqueue(spider_start_iter(spider), spider=name)

        self.started = True

    def stop(self):
        # Detaching spiders
        for spider in self.__spiders.values():
            spider.detach()

        self.stopped = True

        if self.process_pool is not None:
            self.process_pool.terminate()

        self.executor.shutdown(wait=self.executor.wait)

        self.queue.close()

        if self.url_cache:
            self.url_cache.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()

    @overload
    def crawl(
        self,
        callback: None = ...,
    ) -> Iterator[AnyCrawlResult[CrawlJobDataTypes, CrawlResultDataTypes]]:
        ...

    @overload
    def crawl(
        self,
        callback: Callable[
            [
                "Crawler",
                SuccessfulCrawlResult[CrawlJobDataTypes, CrawlResultDataTypes],
            ],
            CallbackResultType,
        ] = ...,
    ) -> Iterator[
        Tuple[
            AnyCrawlResult[CrawlJobDataTypes, CrawlResultDataTypes],
            CallbackResultType,
        ]
    ]:
        ...

    def crawl(
        self,
        callback: Optional[
            Callable[
                [
                    "Crawler",
                    SuccessfulCrawlResult[CrawlJobDataTypes, CrawlResultDataTypes],
                ],
                CallbackResultType,
            ]
        ] = None,
    ) -> Union[
        Iterator[AnyCrawlResult[CrawlJobDataTypes, CrawlResultDataTypes]],
        Iterator[
            Tuple[
                AnyCrawlResult[CrawlJobDataTypes, CrawlResultDataTypes],
                CallbackResultType,
            ]
        ],
    ]:
        worker = CrawlWorker(self, callback=callback, **self.worker_kwargs)

        def key(job: CrawlJob) -> Optional[str]:
            return job.group

        imap_unordered = self.executor.imap_unordered(
            self.queue, worker, key=key, **self.imap_kwargs
        )

        for item in imap_unordered:
            if item is None:
                continue

            result, callback_result = item

            if callback is not None:
                yield result, callback_result  # type: ignore
            else:
                yield result

            self.queue.task_done(result.job)

        # If iterator ended properly we cleanup the queue
        self.queue.cleanup()

    def __iter__(
        self,
    ) -> Iterator[AnyCrawlResult[CrawlJobDataTypes, CrawlResultDataTypes]]:
        return self.crawl()

    def enqueue(
        self,
        target_or_targets: Union[
            UrlOrCrawlTarget[CrawlJobDataTypes],
            Iterable[UrlOrCrawlTarget[CrawlJobDataTypes]],
        ],
        spider: Optional[str] = None,
        depth: Optional[int] = None,
        base_url: Optional[str] = None,
        parent: Optional[CrawlJob[CrawlJobDataTypes]] = None,
    ) -> int:
        with self.enqueue_lock:
            if isinstance(target_or_targets, (str, CrawlTarget)):
                targets = [target_or_targets]
            else:
                targets = target_or_targets

            # NOTE: we consume jobs early and before actually enqueuing to
            # catch errors early.
            # NOTE: this means that enqueue is basically the only place allowed
            # to build CrawlJob instances and validate them.
            jobs = []

            for target in targets:
                if isinstance(target, str):
                    job = CrawlJob(url=target)
                elif isinstance(target, CrawlTarget):
                    job = CrawlJob(
                        url=target.url,
                        depth=target.depth,
                        spider=target.spider,
                        priority=target.priority,
                        data=target.data,
                    )
                else:
                    raise TypeError(
                        "attempted to enqueue a target with an invalid type %s, while expecting str or CrawlTarget"
                        % target.__class__.__name__
                    )

                job.url = ensure_protocol(job.url.strip(), "https")

                if base_url is not None:
                    job.url = urljoin(base_url, job.url)

                job.group = get_domain_name(job.url)

                if spider is not None and job.spider is None:
                    job.spider = spider

                if job.spider is not None and job.spider not in self.__spiders:
                    raise UnknownSpiderError(job.spider)

                if depth is not None:
                    job.depth = depth

                if parent is not None:
                    job.parent = parent.id

                jobs.append(job)

            # Filtering urls we already visited
            if self.url_cache is not None:
                jobs = self.url_cache.register(jobs)

            count = len(jobs)

            self.queue.put_many(jobs)
            self.state.inc_queued(count)

            return count

    def write(
        self,
        filename: str,
        contents: Union[str, bytes],
        compress: bool = False,
        relative: bool = False,
    ) -> str:
        return self.file_writer.write(
            filename, contents, compress=compress, relative=relative
        )

    def submit(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        # NOTE: this might be a footgun!
        if self.process_pool is None:
            return fn(*args, **kwargs)

        return self.process_pool.apply(fn, args, kwargs)
