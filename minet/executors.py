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
    Any,
)
from minet.types import Literal

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
AddendumType = TypeVar("AddendumType")

CANCELLED = object()


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


class RequestResult(Generic[ItemType, AddendumType]):
    __slots__ = ("item", "url", "error", "response", "addendum")

    item: ItemType
    url: Optional[str]
    error: Optional[Exception]
    response: Optional[Response]
    addendum: Optional[AddendumType]

    def __init__(self, item: ItemType, url: Optional[str]):
        self.item = item
        self.url = url
        self.error = None
        self.response = None
        self.addendum = None

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


class PassthroughRequestResult(RequestResult[ItemType, None]):
    item: ItemType
    url: None
    error: None
    response: None
    addendum: None

    def __init__(self, item: ItemType):
        self.item = item
        self.url = None
        self.error = None
        self.response = None
        self.addendum = None

    @property
    def error_code(self) -> None:
        return None


class ErroredRequestResult(RequestResult[ItemType, None]):
    item: ItemType
    url: str
    error: Exception
    response: None
    addendum: None

    def __init__(self, item: ItemType, url: str, error: Exception):
        self.item = item
        self.url = url
        self.error = error
        self.response = None
        self.addendum = None

    @property
    def error_code(self) -> str:
        return serialize_error_as_slug(self.error)


class SuccessfulRequestResult(RequestResult[ItemType, AddendumType]):
    item: ItemType
    url: str
    error: None
    response: Response
    addendum: AddendumType

    def __init__(
        self, item: ItemType, url: str, response: Response, addendum: AddendumType
    ):
        self.item = item
        self.url = url
        self.error = None
        self.response = response
        self.addendum = addendum

    @property
    def error_code(self) -> None:
        return None


AnyRequestResult = Union[
    PassthroughRequestResult[ItemType],
    ErroredRequestResult[ItemType],
    SuccessfulRequestResult[ItemType, AddendumType],
]
AnyActualRequestResult = Union[
    ErroredRequestResult[ItemType], SuccessfulRequestResult[ItemType, AddendumType]
]


class ResolveResult(Generic[ItemType, AddendumType]):
    __slots__ = ("item", "url", "error", "stack", "addendum")

    item: ItemType
    url: Optional[str]
    error: Optional[Exception]
    stack: Optional[RedirectionStack]
    addendum: Optional[AddendumType]

    def __init__(self, item: ItemType, url: Optional[str]):
        self.item = item
        self.url = url
        self.error = None
        self.stack = None
        self.addendum = None

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


class PassthroughResolveResult(ResolveResult[ItemType, None]):
    item: ItemType
    url: None
    error: None
    stack: None
    addendum: None

    def __init__(self, item: ItemType):
        self.item = item
        self.url = None
        self.error = None
        self.stack = None
        self.addendum = None

    @property
    def error_code(self) -> None:
        return None


class ErroredResolveResult(ResolveResult[ItemType, None]):
    item: ItemType
    url: str
    error: Exception
    stack: None
    addendum: None

    def __init__(self, item: ItemType, url: str, error: Exception):
        self.item = item
        self.url = url
        self.error = error
        self.stack = None
        self.addendum = None

    @property
    def error_code(self) -> str:
        return serialize_error_as_slug(self.error)


class SuccessfulResolveResult(ResolveResult[ItemType, AddendumType]):
    item: ItemType
    url: str
    error: None
    stack: RedirectionStack
    addendum: AddendumType

    def __init__(
        self, item: ItemType, url: str, stack: RedirectionStack, addendum: AddendumType
    ):
        self.item = item
        self.url = url
        self.error = None
        self.stack = stack
        self.addendum = addendum

    @property
    def error_code(self) -> None:
        return None


AnyResolveResult = Union[
    PassthroughResolveResult[ItemType],
    ErroredResolveResult[ItemType],
    SuccessfulResolveResult[ItemType, AddendumType],
]
AnyActualResolveResult = Union[
    ErroredResolveResult[ItemType], SuccessfulResolveResult[ItemType, AddendumType]
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


class HTTPWorker(Generic[ItemType, AddendumType]):
    def __init__(
        self,
        pool_manager: urllib3.PoolManager,
        cancel_event: Event,
        local_context: threading.local,
        *,
        resolving: bool = False,
        get_args: Optional[ArgsCallbackType[ItemType]] = None,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        follow_refresh_header: bool = True,
        follow_meta_refresh: bool = False,
        follow_js_relocation: bool = False,
        infer_redirection: bool = False,
        canonicalize: bool = False,
        callback: Optional[
            Callable[[ItemType, str, Union[Response, RedirectionStack]], AddendumType]
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

    def __call__(
        self, payload: HTTPWorkerPayloadBase[ItemType]
    ) -> Union[object, RequestResult[ItemType, AddendumType]]:
        item, url = payload.item, payload.url

        # Noop
        if url is None:
            return self.PassthroughResult(item)

        kwargs = {}

        if self.cancel_event.is_set():
            return CANCELLED

        if self.get_args is not None:
            # NOTE: given callback must be threadsafe
            kwargs = self.get_args(cast(HTTPWorkerPayload, payload))

        if self.cancel_event.is_set():
            return CANCELLED

        try:
            retryer = getattr(self.local_context, "retryer", None)
            kwargs.update(self.default_kwargs)

            if retryer is not None:
                output = retryer(self.fn, url, **kwargs)
            else:
                output = self.fn(url, **kwargs)

        except CancelledRequestError:
            return CANCELLED

        except EXPECTED_WEB_ERRORS as error:
            return self.ErroredResult(item, url, error)

        else:
            addendum = None

            if self.callback is not None:
                if self.cancel_event.is_set():
                    return CANCELLED

                try:
                    if retryer is not None:
                        addendum = retryer(self.callback, item, url, output)
                    else:
                        addendum = self.callback(item, url, output)
                except Exception as reason:
                    return self.ErroredResult(item, url, HTTPCallbackError(reason))

        return self.SuccessfulResult(item, url, output, addendum)  # type: ignore


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
            num_pools=1024,
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
        ordered: bool = ...,
        key: Optional[Callable[[ItemType], Optional[str]]] = ...,
        throttle: float = ...,
        request_args: Optional[ArgsCallbackType[ItemType]] = ...,
        buffer_size: int = ...,
        domain_parallelism: int = ...,
        max_redirects: int = ...,
        callback: Optional[Callable[[ItemType, str, Response], AddendumType]] = ...,
        passthrough: Literal[False] = False,
    ) -> Iterator[AnyActualRequestResult[ItemType, AddendumType]]:
        ...

    @overload
    def request(
        self,
        iterator: Iterable[ItemType],
        *,
        ordered: bool = ...,
        key: Optional[Callable[[ItemType], Optional[str]]] = ...,
        throttle: float = ...,
        request_args: Optional[ArgsCallbackType[ItemType]] = ...,
        buffer_size: int = ...,
        domain_parallelism: int = ...,
        max_redirects: int = ...,
        callback: Optional[Callable[[ItemType, str, Response], AddendumType]] = ...,
        passthrough: Literal[True] = ...,
    ) -> Iterator[AnyRequestResult[ItemType, AddendumType]]:
        ...

    def request(
        self,
        iterator: Iterable[ItemType],
        *,
        ordered: bool = False,
        key: Optional[Callable[[ItemType], Optional[str]]] = None,
        throttle: float = DEFAULT_THROTTLE,
        request_args: Optional[ArgsCallbackType[ItemType]] = None,
        buffer_size: int = DEFAULT_IMAP_BUFFER_SIZE,
        domain_parallelism: int = DEFAULT_DOMAIN_PARALLELISM,
        max_redirects: int = DEFAULT_FETCH_MAX_REDIRECTS,
        callback: Optional[Callable[[ItemType, str, Response], AddendumType]] = None,
        passthrough: bool = False,
    ) -> Iterator[
        Union[
            AnyRequestResult[ItemType, AddendumType],
            AnyActualRequestResult[ItemType, AddendumType],
        ]
    ]:
        # TODO: validate
        worker = HTTPWorker(
            self.pool_manager,
            self.cancel_event,
            self.local_context,
            get_args=request_args,
            max_redirects=max_redirects,
            callback=callback,
        )

        method = super().imap if ordered else super().imap_unordered

        imap_unordered = method(
            payloads_iter(iterator, key=key, passthrough=passthrough),
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )

        return (item for item in imap_unordered if item is not CANCELLED)  # type: ignore

    @overload
    def resolve(
        self,
        iterator: Iterable[ItemType],
        *,
        ordered: bool = ...,
        key: Optional[Callable[[ItemType], Optional[str]]] = ...,
        throttle: float = ...,
        resolve_args: Optional[ArgsCallbackType[ItemType]] = ...,
        buffer_size: int = ...,
        domain_parallelism: int = ...,
        max_redirects: int = ...,
        follow_refresh_header: bool = ...,
        follow_meta_refresh: bool = ...,
        follow_js_relocation: bool = ...,
        infer_redirection: bool = ...,
        canonicalize: bool = ...,
        callback: Optional[
            Callable[[ItemType, str, RedirectionStack], AddendumType]
        ] = ...,
        passthrough: Literal[False] = False,
    ) -> Iterator[AnyActualResolveResult[ItemType, AddendumType]]:
        ...

    @overload
    def resolve(
        self,
        iterator: Iterable[ItemType],
        *,
        ordered: bool = ...,
        key: Optional[Callable[[ItemType], Optional[str]]] = ...,
        throttle: float = ...,
        resolve_args: Optional[ArgsCallbackType[ItemType]] = ...,
        buffer_size: int = ...,
        domain_parallelism: int = ...,
        max_redirects: int = ...,
        follow_refresh_header: bool = ...,
        follow_meta_refresh: bool = ...,
        follow_js_relocation: bool = ...,
        infer_redirection: bool = ...,
        canonicalize: bool = ...,
        callback: Optional[
            Callable[[ItemType, str, RedirectionStack], AddendumType]
        ] = ...,
        passthrough: Literal[True] = ...,
    ) -> Iterator[AnyResolveResult[ItemType, AddendumType]]:
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
            Callable[[ItemType, str, RedirectionStack], AddendumType]
        ] = None,
        passthrough: bool = False,
    ) -> Iterator[
        Union[
            AnyResolveResult[ItemType, AddendumType],
            AnyActualResolveResult[ItemType, AddendumType],
        ]
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

        imap_unordered = method(
            payloads_iter(iterator, key=key, passthrough=passthrough),
            worker,
            key=key_by_domain_name,
            parallelism=domain_parallelism,
            buffer_size=buffer_size,
            throttle=throttle,
        )

        return (item for item in imap_unordered if item is not CANCELLED)  # type: ignore
