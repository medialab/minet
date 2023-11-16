# =============================================================================
# Minet HTTP Multithreaded Executors
# =============================================================================
#
# Exposing a specialized quenouille wrapper grabbing various urls from the
# web in a multithreaded fashion.
#
from typing import (
    cast,
    overload,
    Optional,
    Iterator,
    Callable,
    TypeVar,
    Generic,
    Iterable,
    Dict,
    Union,
    Tuple,
    Awaitable,
    Any,
    TYPE_CHECKING,
)
from minet.types import Literal, TypedDict, Unpack, NotRequired

if TYPE_CHECKING:
    from minet.browser.threadsafe_browser import BrowserOrBrowserContext

import urllib3
import threading
from threading import Event
from quenouille import ThreadPoolExecutor
from ural import get_domain_name, ensure_protocol
from tenacity import RetryCallState

from minet.serialization import serialize_error_as_slug
from minet.exceptions import CancelledRequestError, HTTPCallbackError
from minet.web import (
    create_pool_manager,
    create_request_retryer,
    request,
    resolve,
    Response,
    RedirectionStack,
    AnyTimeout,
    EXPECTED_WEB_ERRORS,
)
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
CallbackResultType = TypeVar("CallbackResultType")


class HTTPWorkerPayloadBase(Generic[ItemType]):
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


class HTTPWorkerPayload(HTTPWorkerPayloadBase[ItemType]):
    item: ItemType
    url: str


ArgsCallbackType = Callable[[HTTPWorkerPayload[ItemType]], Dict]


class ExecutorRequestKwargs(TypedDict, Generic[ItemType, CallbackResultType]):
    ordered: NotRequired[bool]
    key: NotRequired[Optional[Callable[[ItemType], Optional[str]]]]
    throttle: NotRequired[float]
    request_args: NotRequired[Optional[ArgsCallbackType[ItemType]]]
    use_pycurl: NotRequired[bool]
    compressed: NotRequired[bool]
    buffer_size: NotRequired[int]
    domain_parallelism: NotRequired[int]
    max_redirects: NotRequired[int]
    known_encoding: NotRequired[Optional[str]]


class ExecutorResolveKwargs(TypedDict, Generic[ItemType, CallbackResultType]):
    ordered: NotRequired[bool]
    key: NotRequired[Optional[Callable[[ItemType], Optional[str]]]]
    throttle: NotRequired[float]
    resolve_args: NotRequired[Optional[ArgsCallbackType[ItemType]]]
    buffer_size: NotRequired[int]
    domain_parallelism: NotRequired[int]
    max_redirects: NotRequired[int]
    follow_refresh_header: NotRequired[bool]
    follow_meta_refresh: NotRequired[bool]
    follow_js_relocation: NotRequired[bool]
    infer_redirection: NotRequired[bool]
    canonicalize: NotRequired[bool]


class RequestResult(Generic[ItemType]):
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

    @property
    def error_code(self) -> Optional[str]:
        return serialize_error_as_slug(self.error) if self.error is not None else None

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


class PassthroughRequestResult(RequestResult[ItemType]):
    item: ItemType
    url: None
    error: None
    response: None

    def __init__(self, item: ItemType):
        self.item = item
        self.url = None
        self.error = None
        self.response = None

    @property
    def error_code(self) -> None:
        return None


class ErroredRequestResult(RequestResult[ItemType]):
    item: ItemType
    url: str
    error: Exception
    response: None

    def __init__(self, item: ItemType, url: str, error: Exception):
        self.item = item
        self.url = url
        self.error = error
        self.response = None

    @property
    def error_code(self) -> str:
        return serialize_error_as_slug(self.error)


class SuccessfulRequestResult(RequestResult[ItemType]):
    item: ItemType
    url: str
    error: None
    response: Response

    def __init__(self, item: ItemType, url: str, response: Response):
        self.item = item
        self.url = url
        self.error = None
        self.response = response

    @property
    def error_code(self) -> None:
        return None


AnyActualRequestResult = Union[
    ErroredRequestResult[ItemType], SuccessfulRequestResult[ItemType]
]

AnyRequestResult = Union[
    AnyActualRequestResult[ItemType], PassthroughRequestResult[ItemType]
]


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

    @property
    def error_code(self) -> Optional[str]:
        return serialize_error_as_slug(self.error) if self.error is not None else None

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


class PassthroughResolveResult(ResolveResult[ItemType]):
    item: ItemType
    url: None
    error: None
    stack: None

    def __init__(self, item: ItemType):
        self.item = item
        self.url = None
        self.error = None
        self.stack = None

    @property
    def error_code(self) -> None:
        return None


class ErroredResolveResult(ResolveResult[ItemType]):
    item: ItemType
    url: str
    error: Exception
    stack: None

    def __init__(self, item: ItemType, url: str, error: Exception):
        self.item = item
        self.url = url
        self.error = error
        self.stack = None

    @property
    def error_code(self) -> str:
        return serialize_error_as_slug(self.error)


class SuccessfulResolveResult(ResolveResult[ItemType]):
    item: ItemType
    url: str
    error: None
    stack: RedirectionStack

    def __init__(self, item: ItemType, url: str, stack: RedirectionStack):
        self.item = item
        self.url = url
        self.error = None
        self.stack = stack

    @property
    def error_code(self) -> None:
        return None


AnyActualResolveResult = Union[
    ErroredResolveResult[ItemType], SuccessfulResolveResult[ItemType]
]

AnyResolveResult = Union[
    AnyActualResolveResult[ItemType], PassthroughResolveResult[ItemType]
]


def key_by_domain_name(payload: HTTPWorkerPayloadBase) -> Optional[str]:
    return payload.domain


def payloads_iter(
    iterable: Iterable[ItemType],
    key: Optional[Callable[[ItemType], Optional[str]]] = None,
    passthrough: bool = False,
) -> Iterator[HTTPWorkerPayloadBase[ItemType]]:
    for item in iterable:
        url = item if key is None else key(item)

        if not url:
            if not passthrough:
                raise TypeError("item has no url: {!r}".format(item))

            yield HTTPWorkerPayloadBase(item=item, url=None)
            continue

        # Url cleanup
        url = ensure_protocol(url.strip())  # type: ignore

        yield HTTPWorkerPayloadBase(item=item, url=url)


class HTTPWorker(Generic[ItemType, CallbackResultType]):
    def __init__(
        self,
        pool_manager: urllib3.PoolManager,
        cancel_event: Event,
        local_context: threading.local,
        *,
        resolving: bool = False,
        get_args: Optional[ArgsCallbackType[ItemType]] = None,
        use_pycurl: bool = False,
        compressed: bool = False,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        follow_refresh_header: bool = True,
        follow_meta_refresh: bool = False,
        follow_js_relocation: bool = False,
        infer_redirection: bool = False,
        canonicalize: bool = False,
        known_encoding: Optional[str] = None,
        callback: Optional[
            Union[
                Callable[[ItemType, str, Response], CallbackResultType],
                Callable[[ItemType, str, RedirectionStack], CallbackResultType],
            ]
        ] = None,
    ):
        self.cancel_event = cancel_event
        self.local_context = local_context
        self.get_args = get_args
        self.callback = callback

        self.resolving = resolving
        self.fn = request if not resolving else resolve
        self.PassthroughResult = (
            PassthroughRequestResult if not resolving else PassthroughResolveResult
        )
        self.SuccessfulResult = (
            SuccessfulRequestResult if not resolving else SuccessfulResolveResult
        )
        self.ErroredResult = (
            ErroredRequestResult if not resolving else ErroredResolveResult
        )

        self.default_kwargs = {
            "pool_manager": pool_manager,
            "max_redirects": max_redirects,
            "cancel_event": cancel_event,
            "follow_refresh_header": follow_refresh_header,
            "follow_meta_refresh": follow_meta_refresh,
            "follow_js_relocation": follow_js_relocation,
            "infer_redirection": infer_redirection,
            "canonicalize": canonicalize,
        }

        if use_pycurl:
            del self.default_kwargs["pool_manager"]
            self.default_kwargs["use_pycurl"] = True

        if compressed:
            self.default_kwargs["compressed"] = True

        if known_encoding is not None:
            self.default_kwargs["known_encoding"] = known_encoding

    def __call__(
        self, payload: HTTPWorkerPayloadBase[ItemType]
    ) -> Optional[
        Tuple[
            Union[
                AnyRequestResult[ItemType],
                AnyResolveResult[ItemType],
            ],
            Optional[CallbackResultType],
        ]
    ]:
        item, url = payload.item, payload.url

        # Noop
        if url is None:
            return self.PassthroughResult(item), None  # type: ignore

        kwargs = self.default_kwargs.copy()

        if self.cancel_event.is_set():
            return

        if self.get_args is not None:
            # NOTE: given callback must be threadsafe
            kwargs.update(self.get_args(cast(HTTPWorkerPayload, payload)))

        if self.cancel_event.is_set():
            return

        try:
            retryer = getattr(self.local_context, "retryer", None)

            if retryer is not None:
                output = retryer(self.fn, url, **kwargs)
            else:
                output = self.fn(url, **kwargs)

        except CancelledRequestError:
            return

        except EXPECTED_WEB_ERRORS as error:
            return self.ErroredResult(item, url, error), None

        else:
            callback_result = None

            if self.callback is not None:
                if self.cancel_event.is_set():
                    return

                try:
                    if retryer is not None:
                        callback_result = retryer(self.callback, item, url, output)
                    else:
                        callback_result = self.callback(item, url, output)  # type: ignore
                except Exception as reason:
                    return (
                        self.ErroredResult(item, url, HTTPCallbackError(reason)),
                        None,
                    )

        return self.SuccessfulResult(item, url, output), callback_result  # type: ignore


class HTTPThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(
        self,
        max_workers: Optional[int] = None,
        wait: bool = True,
        daemonic: bool = False,
        insecure: bool = False,
        timeout: AnyTimeout = DEFAULT_URLLIB3_TIMEOUT,
        spoof_tls_ciphers: bool = False,
        proxy: Optional[str] = None,
        retry: bool = False,
        retryer_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.cancel_event = Event()
        self.local_context = threading.local()

        if retry:

            def epilog(retry_state: RetryCallState) -> str:
                return retry_state.args[0]

            default_retryer_kwargs = {
                "retry_on_timeout": False,
                "cancel_event": self.cancel_event,
                "max_attempts": 3,
                "epilog": epilog,
            }

            default_retryer_kwargs.update(retryer_kwargs or {})

            def init_local_context():
                self.local_context.retryer = create_request_retryer(
                    **default_retryer_kwargs
                )

            kwargs["initializer"] = init_local_context

        super().__init__(
            max_workers,
            wait=wait,
            daemonic=daemonic,
            **kwargs,
        )

        # NOTE: 0 workers means a synchronous pool in quenouille,
        # so we reserve at least one connection for the pool.
        self.pool_manager = create_pool_manager(
            parallelism=max(1, self.max_workers),
            num_pools=max(64, self.max_workers),
            insecure=insecure,
            timeout=timeout,
            spoof_tls_ciphers=spoof_tls_ciphers,
            proxy=proxy,
        )

    def cancel(self) -> None:
        self.cancel_event.set()

    def shutdown(self, wait=True) -> None:
        self.cancel()
        self.pool_manager.clear()
        return super().shutdown(wait=wait)

    @overload
    def request(
        self,
        iterator: Iterable[ItemType],
        *,
        passthrough: Literal[False] = ...,
        callback: None = ...,
        **kwargs: Unpack[ExecutorRequestKwargs[ItemType, CallbackResultType]],
    ) -> Iterator[AnyActualRequestResult[ItemType]]:
        ...

    @overload
    def request(
        self,
        iterator: Iterable[ItemType],
        *,
        passthrough: Literal[True] = ...,
        callback: None = ...,
        **kwargs: Unpack[ExecutorRequestKwargs[ItemType, CallbackResultType]],
    ) -> Iterator[AnyRequestResult[ItemType]]:
        ...

    @overload
    def request(
        self,
        iterator: Iterable[ItemType],
        *,
        passthrough: Literal[False] = ...,
        callback: Callable[[ItemType, str, Response], CallbackResultType] = ...,
        **kwargs: Unpack[ExecutorRequestKwargs[ItemType, CallbackResultType]],
    ) -> Iterator[Tuple[AnyActualRequestResult[ItemType], CallbackResultType]]:
        ...

    @overload
    def request(
        self,
        iterator: Iterable[ItemType],
        *,
        passthrough: Literal[True] = ...,
        callback: Callable[[ItemType, str, Response], CallbackResultType] = ...,
        **kwargs: Unpack[ExecutorRequestKwargs[ItemType, CallbackResultType]],
    ) -> Iterator[Tuple[AnyRequestResult[ItemType], CallbackResultType]]:
        ...

    def request(
        self,
        iterator: Iterable[ItemType],
        *,
        ordered: bool = False,
        key: Optional[Callable[[ItemType], Optional[str]]] = None,
        throttle: float = DEFAULT_THROTTLE,
        request_args: Optional[ArgsCallbackType[ItemType]] = None,
        use_pycurl: bool = False,
        compressed: bool = False,
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        known_encoding: Optional[str] = None,
        callback: Optional[
            Callable[[ItemType, str, Response], CallbackResultType]
        ] = None,
        passthrough: bool = False,
    ) -> Union[
        Iterator[AnyRequestResult[ItemType]],
        Iterator[AnyActualRequestResult[ItemType]],
        Iterator[Tuple[AnyRequestResult[ItemType], CallbackResultType]],
        Iterator[Tuple[AnyActualRequestResult[ItemType], CallbackResultType]],
    ]:
        # TODO: validate
        worker = HTTPWorker(
            self.pool_manager,
            self.cancel_event,
            self.local_context,
            get_args=request_args,
            max_redirects=max_redirects,
            use_pycurl=use_pycurl,
            compressed=compressed,
            known_encoding=known_encoding,
            callback=callback,
        )

        method = super().imap if ordered else super().imap_unordered

        imap = method(
            payloads_iter(iterator, key=key, passthrough=passthrough),
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )

        for item in imap:
            if item is None:
                continue

            if callback is not None:
                yield item  # type: ignore
            else:
                yield item[0]  # type: ignore

    @overload
    def resolve(
        self,
        iterator: Iterable[ItemType],
        *,
        callback: None = ...,
        passthrough: Literal[False] = ...,
        **kwargs: Unpack[ExecutorResolveKwargs[ItemType, CallbackResultType]],
    ) -> Iterator[AnyActualResolveResult[ItemType]]:
        ...

    @overload
    def resolve(
        self,
        iterator: Iterable[ItemType],
        *,
        callback: None = ...,
        passthrough: Literal[True] = ...,
        **kwargs: Unpack[ExecutorResolveKwargs[ItemType, CallbackResultType]],
    ) -> Iterator[AnyResolveResult[ItemType]]:
        ...

    @overload
    def resolve(
        self,
        iterator: Iterable[ItemType],
        *,
        callback: Callable[[ItemType, str, RedirectionStack], CallbackResultType],
        passthrough: Literal[False] = ...,
        **kwargs: Unpack[ExecutorResolveKwargs[ItemType, CallbackResultType]],
    ) -> Iterator[Tuple[AnyActualResolveResult[ItemType], CallbackResultType]]:
        ...

    @overload
    def resolve(
        self,
        iterator: Iterable[ItemType],
        *,
        callback: Callable[[ItemType, str, RedirectionStack], CallbackResultType],
        passthrough: Literal[True] = ...,
        **kwargs: Unpack[ExecutorResolveKwargs[ItemType, CallbackResultType]],
    ) -> Iterator[Tuple[AnyResolveResult[ItemType], CallbackResultType]]:
        ...

    def resolve(
        self,
        iterator: Iterable[ItemType],
        *,
        ordered: bool = False,
        key: Optional[Callable[[ItemType], Optional[str]]] = None,
        throttle: float = DEFAULT_THROTTLE,
        resolve_args: Optional[ArgsCallbackType[ItemType]] = None,
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
        max_redirects: int = DEFAULT_RESOLVE_MAX_REDIRECTS,
        follow_refresh_header: bool = True,
        follow_meta_refresh: bool = False,
        follow_js_relocation: bool = False,
        infer_redirection: bool = False,
        canonicalize: bool = False,
        callback: Optional[
            Callable[[ItemType, str, RedirectionStack], CallbackResultType]
        ] = None,
        passthrough: bool = False,
    ) -> Union[
        Iterator[AnyResolveResult[ItemType]],
        Iterator[AnyActualResolveResult[ItemType]],
        Iterator[Tuple[AnyResolveResult[ItemType], CallbackResultType]],
        Iterator[Tuple[AnyActualResolveResult[ItemType], CallbackResultType]],
    ]:
        # TODO: validate
        worker = HTTPWorker(
            self.pool_manager,
            self.cancel_event,
            self.local_context,
            resolving=True,
            get_args=resolve_args,
            max_redirects=max_redirects,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation,
            infer_redirection=infer_redirection,
            canonicalize=canonicalize,
            callback=callback,
        )

        method = super().imap if ordered else super().imap_unordered

        imap = method(
            payloads_iter(iterator, key=key, passthrough=passthrough),
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )

        for item in imap:
            if item is None:
                continue

            if callback is not None:
                yield item  # type: ignore
            else:
                yield item[0]  # type: ignore


class BrowserThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(
        self,
        max_workers: Optional[int] = None,
        wait: bool = True,
        daemonic: bool = False,
        height: int = 1920,
        width: int = 1080,
        adblock: bool = False,
        automatic_consent: bool = False,
        **kwargs,
    ):
        from minet.browser import ThreadsafeBrowser

        self.browser = ThreadsafeBrowser(
            width=width,
            height=height,
            adblock=adblock,
            automatic_consent=automatic_consent,
        )

        super().__init__(
            max_workers,
            wait=wait,
            daemonic=daemonic,
            **kwargs,
        )

    def __enter__(self):
        self.browser.__enter__()
        return super().__enter__()

    def shutdown(self, wait=True) -> None:
        self.browser.stop()
        return super().shutdown(wait=wait)

    def run(
        self,
        iterator: Iterable[ItemType],
        fn: Callable[
            ["BrowserOrBrowserContext", HTTPWorkerPayload[ItemType]],
            Awaitable[ResultType],
        ],
        *,
        ordered: bool = False,
        key: Optional[Callable[[ItemType], Optional[str]]] = None,
        passthrough: bool = False,
        throttle: float = DEFAULT_THROTTLE,
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
    ) -> Iterator[Tuple[ItemType, Optional[ResultType]]]:
        method = super().imap if ordered else super().imap_unordered

        def worker(
            payload: HTTPWorkerPayloadBase[ItemType],
        ) -> Tuple[ItemType, Optional[ResultType]]:
            if payload.url is None:
                return payload.item, None

            return payload.item, self.browser.run_in_browser_or_default_context(
                fn, cast(HTTPWorkerPayload[ItemType], payload)
            )

        imap = method(
            payloads_iter(iterator, key=key, passthrough=passthrough),
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )

        yield from imap
