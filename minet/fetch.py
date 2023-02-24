# =============================================================================
# Minet Multithreaded Fetch
# =============================================================================
#
# Exposing a specialized quenouille wrapper grabbing various urls from the
# web in a multithreaded fashion.
#
from typing import Optional, Iterator, Callable, TypeVar, Generic, Iterable, Dict, Union

import urllib3
from threading import Event
from quenouille import ThreadPoolExecutor
from ural import get_domain_name, ensure_protocol

from minet.exceptions import CancelledRequestError
from minet.web import (
    create_pool_manager,
    request,
    resolve,
    Response,
    RedirectionStack,
    AnyTimeout,
    EXPECTED_WEB_ERRORS,
)
from minet.heuristics import should_spoof_ua_when_resolving
from minet.constants import (
    DEFAULT_DOMAIN_PARALLELISM,
    DEFAULT_IMAP_BUFFER_SIZE,
    DEFAULT_THROTTLE,
    DEFAULT_URLLIB3_TIMEOUT,
    DEFAULT_FETCH_MAX_REDIRECTS,
    DEFAULT_RESOLVE_MAX_REDIRECTS,
)

ItemType = TypeVar("ItemType")
ResultType = TypeVar("ResultType")

CANCELLED = object()


class FetchWorkerPayload(Generic[ItemType]):
    __slots__ = ("item", "url", "__has_cached_domain", "__domain")

    item: ItemType
    url: Optional[str]

    __has_cached_domain: bool
    __domain: Optional[str]

    def __init__(self, item: ItemType, url: Optional[str]):
        self.item = item
        self.url = url
        self.__has_cached_domain = False
        self.__domain = None

    @property
    def domain(self) -> Optional[str]:
        if self.__has_cached_domain:
            return self.__domain

        if self.url is not None:
            self.__domain = get_domain_name(self.url)

        self.__has_cached_domain = True

        return self.__domain


RequestArgsType = Callable[[FetchWorkerPayload[ItemType]], Dict]


class FetchResult(Generic[ItemType]):
    __slots__ = ("item", "url", "error", "response")

    item: ItemType
    url: Optional[str]
    error: Optional[Exception]
    response: Optional[Response]

    def __init__(self, item: ItemType, url: Optional[str]):
        self.item = item
        self.url = url
        self.error = None
        self.response = None

    def __repr__(self):
        name = self.__class__.__name__

        if not self.url:
            return "<{name} null!>".format(name=name)

        if not self.response:
            return "<{name} url={url!r} pending!>".format(name=name, url=self.url)

        if self.error:
            return "<{name} url={url!r} error={error}>".format(
                name=name, url=self.url, error=self.error.__class__.__name__
            )

        assert self.response is not None

        return "<{name} url={url!r} status={status!r}>".format(
            name=name, url=self.url, status=self.response.status
        )


class ResolveResult(Generic[ItemType]):
    __slots__ = ("item", "url", "error", "stack")

    item: ItemType
    url: Optional[str]
    error: Optional[Exception]
    stack: Optional[RedirectionStack]

    def __init__(self, item: ItemType, url: Optional[str]):
        self.item = item
        self.url = url
        self.error = None
        self.stack = None

    def __repr__(self):
        name = self.__class__.__name__

        if not self.url:
            return "<{name} null!>".format(name=name)

        if self.error:
            return "<{name} url={url!r} error={error}>".format(
                name=name, url=self.url, error=self.error.__class__.__name__
            )

        assert self.stack is not None

        return "<{name} url={url!r} status={status!r} redirects={redirects!r}>".format(
            name=name,
            url=self.url,
            status=self.stack[-1].status,
            redirects=len(self.stack),
        )


def key_by_domain_name(payload: FetchWorkerPayload) -> Optional[str]:
    return payload.domain


def payloads_iter(
    iterable: Iterable[ItemType],
    key: Optional[Callable[[ItemType], Optional[str]]] = None,
) -> Iterator[FetchWorkerPayload[ItemType]]:
    for item in iterable:
        url = item if key is None else key(item)

        if not url:
            yield FetchWorkerPayload(item=item, url=None)
            continue

        # Url cleanup
        url = ensure_protocol(url.strip())  # type: ignore

        yield FetchWorkerPayload(item=item, url=url)


class FetchWorker(Generic[ItemType]):
    def __init__(
        self,
        pool_manager: urllib3.PoolManager,
        cancel_event: Event,
        *,
        request_args: Optional[RequestArgsType[ItemType]] = None,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        callback: Optional[Callable[[FetchResult[ItemType]], None]] = None
    ):
        self.pool_manager = pool_manager
        self.cancel_event = cancel_event
        self.request_args = request_args
        self.max_redirects = max_redirects
        self.callback = callback

    def __call__(
        self, payload: FetchWorkerPayload[ItemType]
    ) -> Union[object, FetchResult[ItemType]]:
        item, url = payload.item, payload.url

        result = FetchResult(item, url)

        # Noop
        if url is None:
            return result

        # NOTE: request_args must be threadsafe
        kwargs = {}

        if self.cancel_event.is_set():
            return CANCELLED

        if self.request_args is not None:
            kwargs = self.request_args(payload)

        if self.cancel_event.is_set():
            return CANCELLED

        try:
            response = request(
                url,
                pool_manager=self.pool_manager,
                max_redirects=self.max_redirects,
                cancel_event=self.cancel_event,
                **kwargs
            )

        except CancelledRequestError:
            return CANCELLED

        except EXPECTED_WEB_ERRORS as error:
            result.error = error

        else:
            result.response = response

            if self.callback is not None:
                if self.cancel_event.is_set():
                    return CANCELLED

                self.callback(result)

        return result


class ResolveWorker(Generic[ItemType]):
    def __init__(
        self,
        pool_manager: urllib3.PoolManager,
        cancel_event: Event,
        *,
        resolve_args: Optional[RequestArgsType[ItemType]] = None,
        max_redirects: int = DEFAULT_RESOLVE_MAX_REDIRECTS,
        follow_refresh_header: bool = True,
        follow_meta_refresh: bool = False,
        follow_js_relocation: bool = False,
        infer_redirection: bool = False,
        canonicalize: bool = False
    ):
        self.pool_manager = pool_manager
        self.cancel_event = cancel_event
        self.resolve_args = resolve_args
        self.max_redirects = max_redirects
        self.follow_refresh_header = follow_refresh_header
        self.follow_meta_refresh = follow_meta_refresh
        self.follow_js_relocation = follow_js_relocation
        self.infer_redirection = infer_redirection
        self.canonicalize = canonicalize

    def __call__(
        self, payload: FetchWorkerPayload[ItemType]
    ) -> Union[object, ResolveResult[ItemType]]:
        item, url = payload.item, payload.url

        result = ResolveResult(item, url)

        # Noop
        if url is None:
            return result

        # NOTE: resolve_args must be threadsafe
        kwargs = {}

        if self.cancel_event.is_set():
            return CANCELLED

        if self.resolve_args is not None:
            kwargs = self.resolve_args(payload)

        if self.cancel_event.is_set():
            return CANCELLED

        # NOTE: should it be just in the CLI?
        if "spoof_ua" not in kwargs and payload.domain is not None:
            kwargs["spoof_ua"] = should_spoof_ua_when_resolving(payload.domain)

        try:
            stack = resolve(
                url,
                pool_manager=self.pool_manager,
                max_redirects=self.max_redirects,
                follow_refresh_header=self.follow_refresh_header,
                follow_meta_refresh=self.follow_meta_refresh,
                follow_js_relocation=self.follow_js_relocation,
                infer_redirection=self.infer_redirection,
                canonicalize=self.canonicalize,
                **kwargs
            )
        except CancelledRequestError:
            return CANCELLED
        except EXPECTED_WEB_ERRORS as error:
            result.error = error
        else:
            result.stack = stack

        return result


class HTTPThreadPoolExecutor(ThreadPoolExecutor[ItemType, Optional[str], ResultType]):
    def __init__(
        self,
        max_workers: Optional[int] = None,
        insecure: bool = False,
        timeout: AnyTimeout = DEFAULT_URLLIB3_TIMEOUT,
        **kwargs
    ):
        super().__init__(max_workers, **kwargs)
        self.pool_manager = create_pool_manager(
            threads=max_workers, insecure=insecure, timeout=timeout
        )
        self.cancel_event = Event()

    def cancel(self) -> None:
        self.cancel_event.set()

    def shutdown(self, wait=True) -> None:
        self.cancel()
        self.pool_manager.clear()
        return super().shutdown(wait=wait)

    def imap(self, *args, **kwargs):
        raise NotImplementedError


class FetchThreadPoolExecutor(
    HTTPThreadPoolExecutor[FetchWorkerPayload[ItemType], FetchResult[ItemType]]
):
    def imap_unordered(
        self,
        iterator: Iterable[ItemType],
        *,
        key: Optional[Callable[[ItemType], Optional[str]]] = None,
        throttle: float = DEFAULT_THROTTLE,
        request_args: Optional[RequestArgsType[ItemType]] = None,
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        callback: Optional[Callable[[FetchResult[ItemType]], None]] = None
    ) -> Iterator[FetchResult[ItemType]]:

        # TODO: validate
        worker = FetchWorker(
            self.pool_manager,
            self.cancel_event,
            request_args=request_args,
            max_redirects=max_redirects,
            callback=callback,
        )

        imap_unordered = super().imap_unordered(
            payloads_iter(iterator, key=key),
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )

        return (item for item in imap_unordered if item is not CANCELLED)


class ResolveThreadPoolExecutor(
    HTTPThreadPoolExecutor[FetchWorkerPayload[ItemType], ResolveResult[ItemType]]
):
    def imap_unordered(
        self,
        iterator: Iterable[ItemType],
        *,
        key: Optional[Callable[[ItemType], Optional[str]]] = None,
        throttle: float = DEFAULT_THROTTLE,
        resolve_args: Optional[RequestArgsType[ItemType]] = None,
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        follow_refresh_header: bool = True,
        follow_meta_refresh: bool = False,
        follow_js_relocation: bool = False,
        infer_redirection: bool = False,
        canonicalize: bool = False
    ) -> Iterator[ResolveResult[ItemType]]:

        # TODO: validate
        worker = ResolveWorker(
            self.pool_manager,
            self.cancel_event,
            resolve_args=resolve_args,
            max_redirects=max_redirects,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation,
            infer_redirection=infer_redirection,
            canonicalize=canonicalize,
        )

        imap_unordered = super().imap_unordered(
            payloads_iter(iterator, key=key),
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )

        return (item for item in imap_unordered if item is not CANCELLED)


def multithreaded_fetch(
    iterator: Iterable[ItemType],
    key: Optional[Callable[[ItemType], Optional[str]]] = None,
    request_args: Optional[RequestArgsType[ItemType]] = None,
    threads: int = 25,
    throttle: float = DEFAULT_THROTTLE,
    buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
    insecure: bool = False,
    timeout: AnyTimeout = DEFAULT_URLLIB3_TIMEOUT,
    domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
    max_redirects: int = 5,
    wait: bool = True,
    daemonic: bool = False,
    callback=None,
) -> Iterator[FetchResult[ItemType]]:
    """
    Function returning a multithreaded iterator over fetched urls.

    Args:
        iterator (iterable): An iterator over urls or arbitrary items.
        key (callable, optional): Function extracting url from yielded items.
        request_args (callable, optional): Function returning specific
            arguments to pass to the request util per yielded item.
        threads (int, optional): Number of threads to use. Defaults to 25.
        throttle (float or callable, optional): Per-domain throttle in seconds.
            Or a function taking domain name and item and returning the
            throttle to apply. Defaults to 0.2.
        max_redirects (int, optional): Max number of redirections to follow.
        domain_parallelism (int, optional): Max number of urls per domain to
            hit at the same time. Defaults to 1.
        buffer_size (int, optional): Max number of items per domain to enqueue
            into memory in hope of finding a new domain that can be processed
            immediately. Defaults to 1.
        insecure (bool, optional): Whether to ignore SSL certification errors
            when performing requests. Defaults to False.
        timeout (float or urllib3.Timeout, optional): Custom timeout for every
            request.

    Yields:
        FetchWorkerResult

    """

    def generator():
        with FetchThreadPoolExecutor(
            max_workers=threads,
            insecure=insecure,
            timeout=timeout,
            wait=wait,
            daemonic=daemonic,
        ) as executor:
            yield from executor.imap_unordered(
                iterator,
                key=key,
                throttle=throttle,
                request_args=request_args,
                buffer_size=buffer_size,
                domain_parallelism=domain_parallelism,
                max_redirects=max_redirects,
                callback=callback,
            )

    return generator()


def multithreaded_resolve(
    iterator: Iterable[ItemType],
    key: Optional[Callable[[ItemType], Optional[str]]] = None,
    resolve_args: Optional[RequestArgsType[ItemType]] = None,
    threads: int = 25,
    throttle: float = DEFAULT_THROTTLE,
    max_redirects: int = 5,
    follow_refresh_header: bool = True,
    follow_meta_refresh: bool = False,
    follow_js_relocation: bool = False,
    infer_redirection: bool = False,
    canonicalize: bool = False,
    buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
    insecure: bool = False,
    timeout: AnyTimeout = DEFAULT_URLLIB3_TIMEOUT,
    domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
    wait: bool = True,
    daemonic: bool = False,
) -> Iterator[ResolveResult[ItemType]]:
    """
    Function returning a multithreaded iterator over resolved urls.

    Args:
        iterator (iterable): An iterator over urls or arbitrary items.
        key (callable, optional): Function extracting url from yielded items.
        resolve_args (callable, optional): Function returning specific
            arguments to pass to the resolve util per yielded item.
        threads (int, optional): Number of threads to use. Defaults to 25.
        throttle (float or callable, optional): Per-domain throttle in seconds.
            Or a function taking domain name and item and returning the
            throttle to apply. Defaults to 0.2.
        max_redirects (int, optional): Max number of redirections to follow.
        follow_refresh_header (bool, optional): Whether to follow refresh
            headers. Defaults to True.
        follow_meta_refresh (bool, optional): Whether to follow meta refresh.
            Defaults to False.
        follow_js_relocation (bool, optional): Whether to follow js relocation.
            Defaults to False.
        infer_redirection (bool, optional): Whether to infer redirections
            heuristically from urls. Defaults to False.
        canonicalize (bool, optional): Whether to extract the canonical url found
            in the html of the web page. Defaults to False.
        buffer_size (int, optional): Max number of items per domain to enqueue
            into memory in hope of finding a new domain that can be processed
            immediately. Defaults to 1.
        insecure (bool, optional): Whether to ignore SSL certification errors
            when performing requests. Defaults to False.
        timeout (float or urllib3.Timeout, optional): Custom timeout for every
            request.
        domain_parallelism (int, optional): Max number of urls per domain to
            hit at the same time. Defaults to 1.

    Yields:
        ResolveWorkerResult

    """

    def generator():
        with ResolveThreadPoolExecutor(
            max_workers=threads,
            insecure=insecure,
            timeout=timeout,
            wait=wait,
            daemonic=daemonic,
        ) as executor:
            yield from executor.imap_unordered(
                iterator,
                key=key,
                throttle=throttle,
                resolve_args=resolve_args,
                buffer_size=buffer_size,
                domain_parallelism=domain_parallelism,
                max_redirects=max_redirects,
                follow_refresh_header=follow_refresh_header,
                follow_meta_refresh=follow_meta_refresh,
                follow_js_relocation=follow_js_relocation,
                infer_redirection=infer_redirection,
                canonicalize=canonicalize,
            )

    return generator()
