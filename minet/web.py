# =============================================================================
# Minet Web Utilities
# =============================================================================
#
# Miscellaneous web-related functions used throughout the library.
#
from typing import (
    Optional,
    Callable,
    Tuple,
    Union,
    OrderedDict,
    List,
    Mapping,
    Any,
    Dict,
    Container,
)
from minet.types import Literal

import re
import cgi
import certifi
import random
import urllib3
import urllib3.exceptions as urllib3_exceptions
import urllib.error
import ural
import json
import mimetypes
import functools
import threading
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
from timeit import default_timer as timer
from io import BytesIO
from threading import Event
from itertools import chain
from urllib.parse import urljoin, quote
from urllib3 import HTTPResponse
from urllib3.util.ssl_ import create_urllib3_context
from ebbe import rcompose, noop, format_filesize, format_repr
from collections import defaultdict
from tenacity import (
    Retrying,
    RetryCallState,
    retry_if_exception_type,
    retry_if_exception,
    stop_after_attempt,
    stop_when_event_set,
    sleep_using_event,
)
from tenacity.wait import wait_base

from minet.scrape.soup import suppress_xml_parsed_as_html_warnings, WonderfulSoup
from minet.encodings import normalize_encoding, infer_encoding
from minet.loggers import sleepers_logger
from minet.utils import is_binary_mimetype
from minet.cookies import dict_to_cookie_string
from minet.exceptions import (
    RedirectError,
    MaxRedirectsError,
    InfiniteRedirectsError,
    InvalidRedirectError,
    BadlyEncodedLocationHeaderError,
    InvalidURLError,
    InvalidStatusError,
    SelfRedirectError,
    CancelledRequestError,
    FinalTimeoutError,
)
from minet.constants import (
    DEFAULT_SPOOFED_UA,
    DEFAULT_SPOOFED_TLS_CIPHERS,
    DEFAULT_URLLIB3_TIMEOUT,
)

mimetypes.init()

# Types
AnyTimeout = Union[float, urllib3.Timeout]

# Handy regexes
CHARSET_RE = re.compile(rb'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I)
PRAGMA_RE = re.compile(rb'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I)
XML_RE = re.compile(rb'^\s*<\?xml.*?encoding=["\']*(.+?)["\'>]', flags=re.I)
NOSCRIPT_RE = re.compile(rb"<noscript[^>]*>.*</noscript[^>]*>", flags=re.I)
META_REFRESH_RE = re.compile(
    rb"""<meta\s+http-equiv=['"]?refresh['"]?\s+content=['"]?([^"']+)['">]?""",
    flags=re.I,
)
JAVASCRIPT_LOCATION_RE = re.compile(
    rb"""(?:window\.)?location(?:\s*=\s*|\.replace\(\s*)['"`](.*?)['"`]"""
)
ESCAPED_SLASH_RE = re.compile(rb"\\\/")
HTML_RE = re.compile(
    rb"^\s*<(?:html|head|body|title|meta|link|span|div|img|ul|ol|[ap!?])", flags=re.I
)
CANONICAL_LINK_RE = re.compile(
    rb'<link\s*[^>]*\s+rel=(?:"\s*canonical\s*"|canonical|\'\s*canonical\s*\')\s+[^>]*\s?/?>'
)
HREF_RE = re.compile(rb'href=(\"[^"]+|\'[^\']+|[^\s]+)>?\s?', flags=re.I)

# Constants
REDIRECT_STATUSES = set(HTTPResponse.REDIRECT_STATUSES)
CONTENT_PREBUFFER_UP_TO = 1024
STREAMING_CHUNK_SIZE: int = 2**12
LARGE_CONTENT_PREBUFFER_UP_TO = 2**16
EXPECTED_WEB_ERRORS = (
    urllib.error.URLError,
    urllib3_exceptions.HTTPError,
    RedirectError,
    InvalidURLError,
    InvalidStatusError,
    FinalTimeoutError,
)

assert CONTENT_PREBUFFER_UP_TO < LARGE_CONTENT_PREBUFFER_UP_TO


def infer_encoding_from_headers(response: urllib3.HTTPResponse) -> Optional[str]:
    content_type_header = response.getheader("content-type")

    if content_type_header is None:
        return None

    parsed_header = cgi.parse_header(content_type_header)

    if len(parsed_header) > 1:
        charset = parsed_header[1].get("charset")

        if charset is not None:
            return charset.lower()

    return None


def infer_encodings_from_xml(
    body: bytes, chunk_size: Optional[int] = CONTENT_PREBUFFER_UP_TO
) -> Dict[str, int]:
    possibilities = defaultdict(list)

    chunk = body

    if chunk_size is not None:
        chunk = body[:chunk_size]

    matches = chain(
        re.findall(CHARSET_RE, chunk),
        re.findall(PRAGMA_RE, chunk),
        re.findall(XML_RE, chunk),
    )

    for match in matches:
        encoding = match.decode().lower()
        possibilities[normalize_encoding(encoding)].append(encoding)

    return {max(names, key=len): len(names) for names in possibilities.values()}


def looks_like_html(html_chunk: bytes) -> bool:
    return HTML_RE.match(html_chunk) is not None


def parse_http_header(header: str) -> Tuple[str, str]:
    key, value = header.split(":", 1)

    return key.strip(), value.strip()


# TODO: take more cases into account...
#   http://www.otsukare.info/2015/03/26/refresh-http-header
def parse_http_refresh(value) -> Optional[Tuple[int, str]]:
    try:
        if isinstance(value, bytes):
            value = value.decode()

        duration, url = value.strip().split(";", 1)

        if not url.lower().strip().startswith("url="):
            return None

        return int(duration), str(url.split("=", 1)[1])
    except Exception:
        return None


def extract_href(value):
    m = HREF_RE.search(value)

    if not m:
        return None

    url = m.group(1)

    try:
        url = url.decode("utf-8")
    except UnicodeDecodeError:
        return None

    return url.strip("\"'") or None


def find_canonical_link(html_chunk: bytes):
    m = CANONICAL_LINK_RE.search(html_chunk)

    if not m:
        return None

    return extract_href(m.group())


def find_meta_refresh(html_chunk: bytes):
    m = META_REFRESH_RE.search(html_chunk)

    if not m:
        return None

    return parse_http_refresh(m.group(1))


def find_javascript_relocation(html_chunk: bytes):
    m = JAVASCRIPT_LOCATION_RE.search(html_chunk)

    if not m:
        return None

    try:
        return ESCAPED_SLASH_RE.sub(b"/", m.group(1)).decode()
    except Exception:
        return None


def create_pool_manager(
    proxy: Optional[str] = None,
    parallelism: int = 1,
    num_pools: Optional[int] = None,
    insecure: bool = False,
    spoof_tls_ciphers: bool = False,
    **kwargs
) -> urllib3.PoolManager:
    """
    Helper function returning a urllib3 pool manager with sane defaults.
    """

    manager_kwargs: Dict[str, Any] = {"timeout": DEFAULT_URLLIB3_TIMEOUT}

    if not insecure:
        manager_kwargs["cert_reqs"] = "CERT_REQUIRED"
        manager_kwargs["ca_certs"] = certifi.where()
    else:
        manager_kwargs["cert_reqs"] = "CERT_NONE"
        # manager_kwargs['assert_hostname'] = False

        urllib3.disable_warnings()

    manager_kwargs["maxsize"] = parallelism

    if num_pools is not None:
        manager_kwargs["num_pools"] = num_pools

    manager_kwargs.update(kwargs)

    if spoof_tls_ciphers:
        manager_kwargs["ssl_context"] = create_urllib3_context(
            ciphers=DEFAULT_SPOOFED_TLS_CIPHERS
        )

    if proxy is not None:
        return urllib3.ProxyManager(proxy, **manager_kwargs)

    return urllib3.PoolManager(**manager_kwargs)


DEFAULT_POOL_MANAGER = create_pool_manager()


def timeout_to_final_time(timeout: AnyTimeout) -> float:
    seconds: float

    if isinstance(timeout, urllib3.Timeout):
        if timeout.total is not None:
            seconds = timeout.total
        else:
            seconds = timeout.connect_timeout + timeout.read_timeout
    else:
        seconds = timeout

    # Some epsilon so sockets can timeout themselves properly
    seconds += 0.01

    return timer() + seconds


def pool_manager_aware_timeout_to_final_time(
    pool_manager: urllib3.PoolManager, timeout: Optional[AnyTimeout]
) -> Optional[float]:
    if timeout is not None:
        return timeout_to_final_time(timeout)

    else:
        pool_manager_timeout = pool_manager.connection_pool_kw.get("timeout")

        if pool_manager_timeout is not None:
            return timeout_to_final_time(pool_manager_timeout)

    return None


def stream_response_body(
    response: urllib3.HTTPResponse,
    body: BytesIO,
    chunk_size: int = STREAMING_CHUNK_SIZE,
    cancel_event: Optional[Event] = None,
    final_time: Optional[float] = None,
    up_to: Optional[int] = None,
) -> bool:
    if cancel_event is not None and cancel_event.is_set():
        raise CancelledRequestError

    if up_to is not None and body.tell() >= up_to:
        return False

    while True:
        data = response.read(chunk_size)

        if not data:
            break

        body.write(data)

        if up_to is not None and body.tell() >= up_to:
            return False

        if cancel_event is not None and cancel_event.is_set():
            raise CancelledRequestError

        if final_time is not None:
            if timer() >= final_time:
                raise FinalTimeoutError

    # This is the only place we know the body has been fully read
    return True


class BufferedResponse(object):
    """
    Class wrapping a urllib3.HTTPResponse and representing a response whose
    body has not been yet fully read.

    It is a low-level representation used in the minet.web module that should
    not leak outside normally.

    It is able to stream a response's body safely all while keeping track of
    a "final" timeout correctly enforced to bypass python socket race condition
    issues on read loops and is also able to be cancelled if required.

    NOTE: this is the user's responsability to close or unwrap the response
    after use. This will be done by __del__ in any case, but don't rely
    on it too much.
    """

    __slots__ = (
        "__inner",
        "__body",
        "__cancel_event",
        "__final_time",
        "__finished",
        "__closed",
    )

    def __init__(
        self,
        response: urllib3.HTTPResponse,
        cancel_event: Optional[Event],
        final_time: Optional[float] = None,
    ):
        self.__inner = response
        self.__cancel_event = cancel_event
        self.__final_time = final_time
        self.__body = BytesIO()
        self.__finished = False
        self.__closed = False

    def __len__(self) -> int:
        return self.__body.getbuffer().nbytes

    def __stream(
        self, chunk_size: int = STREAMING_CHUNK_SIZE, up_to: Optional[int] = None
    ) -> None:
        if self.__closed:
            raise TypeError("buffered response was already closed")

        if self.__finished:
            return

        self.__finished = stream_response_body(
            self.__inner,
            chunk_size=chunk_size,
            cancel_event=self.__cancel_event,
            final_time=self.__final_time,
            body=self.__body,
            up_to=up_to,
        )

    def geturl(self) -> Optional[str]:
        return self.__inner.geturl()

    def getheader(self, name: str, default: Optional[str] = None) -> Optional[str]:
        return self.__inner.getheader(name, default)

    @property
    def status(self) -> int:
        return self.__inner.status

    @property
    def body(self) -> bytes:
        return self.__body.getvalue()

    def close(self) -> None:
        if self.__closed:
            raise TypeError("already closed")

        self.__closed = True

        # urllib3's documentation is not very clear on the subject but it seems
        # the library was not geared toward only reading a few bytes from the
        # body of a request.
        # This means that if we read everything, we should only release the
        # connection so it can be reused by the pool. In the contrary,
        # we need to close the connection to avoid issues. What's more, it
        # is important to close the connection before releasing it.
        # Ref: https://urllib3.readthedocs.io/en/stable/advanced-usage.html#streaming-and-i-o
        if not self.__finished:
            # NOTE: closing connections has a performance cost but I am
            # not really able to understand whether it would be safe not
            # to close them at all.
            self.__inner.close()

        self.__inner.release_conn()

    def __del__(self):
        if not self.__closed:
            # warnings.warn("BufferedResponse instance was not properly closed!")
            self.close()

    def unwrap(self) -> Tuple[urllib3.HTTPResponse, bytes]:
        self.close()
        return self.__inner, self.__body.getvalue()

    def read(self, chunk_size: int = STREAMING_CHUNK_SIZE) -> None:
        self.__stream(chunk_size=chunk_size)

    def read_and_unwrap(self) -> Tuple[urllib3.HTTPResponse, bytes]:
        self.read()
        return self.unwrap()

    def prebuffer_up_to(
        self, amount: int, chunk_size: int = STREAMING_CHUNK_SIZE
    ) -> None:
        self.__stream(chunk_size=chunk_size, up_to=amount)


def atomic_request(
    pool_manager: urllib3.PoolManager,
    url: str,
    method="GET",
    headers=None,
    timeout=None,
    body=None,
    cancel_event: Optional[Event] = None,
    final_time: Optional[float] = None,
) -> BufferedResponse:
    """
    Generic request helpers using a urllib3 pool_manager to access some resource.
    """

    # Validating URL
    if not ural.is_url(
        url, require_protocol=True, tld_aware=True, allow_spaces_in_path=True
    ):
        raise InvalidURLError(url)

    # We check for cancellation
    if cancel_event is not None and cancel_event.is_set():
        raise CancelledRequestError

    # Performing request
    request_kwargs = {
        "headers": headers,
        "body": body,
        "preload_content": False,
        "decode_content": False,
        "release_conn": False,
        "redirect": False,
        "retries": False,
    }

    if timeout is not None:
        request_kwargs["timeout"] = timeout

    if final_time is None:
        final_time = pool_manager_aware_timeout_to_final_time(pool_manager, timeout)

    response = pool_manager.request(method, url, **request_kwargs)

    return BufferedResponse(response, cancel_event=cancel_event, final_time=final_time)


RedirectionType = Literal[
    "hit",
    "location-header",
    "js-relocation",
    "refresh-header",
    "meta-refresh",
    "infer",
    "canonical",
]


class Redirection(object):
    __slots__ = ("status", "type", "url")

    status: Optional[int]
    url: str
    type: RedirectionType

    def __init__(
        self, url: str, _type: RedirectionType = "hit", status: Optional[int] = None
    ):
        self.status = status
        self.url = url
        self.type = _type

    def __repr__(self):
        class_name = self.__class__.__name__

        return ("<%(class_name)s type=%(type)s status=%(status)s url=%(url)s>") % {
            "class_name": class_name,
            "type": self.type,
            "status": self.status,
            "url": self.url,
        }


RedirectionStack = List[Redirection]


def atomic_resolve(
    pool_manager: urllib3.PoolManager,
    url: str,
    method: str = "GET",
    headers=None,
    max_redirects: int = 5,
    follow_refresh_header: bool = True,
    follow_meta_refresh: bool = False,
    follow_js_relocation: bool = False,
    infer_redirection: bool = False,
    timeout: Optional[AnyTimeout] = None,
    cancel_event: Optional[Event] = None,
    final_time: Optional[float] = None,
    body=None,
    canonicalize: bool = False,
) -> Tuple[RedirectionStack, BufferedResponse]:
    """
    Helper function attempting to resolve the given url.
    """

    url_stack: OrderedDict[str, Redirection] = OrderedDict()
    buffered_response: Optional[BufferedResponse] = None

    if final_time is None:
        final_time = pool_manager_aware_timeout_to_final_time(pool_manager, timeout)

    try:
        for _ in range(max_redirects):
            # We close last buffered_response as it won't be used anymore
            # NOTE: this should always happen at the beginning of the loop
            if buffered_response is not None:
                buffered_response.close()
                # NOTE: resetting variable to avoid double free on errors
                buffered_response = None

            # Detecting cycles
            if url in url_stack:
                raise InfiniteRedirectsError("Infinite redirects")

            if infer_redirection:
                target = ural.infer_redirection(url, recursive=False)

                if target != url:
                    url_stack[url] = Redirection(url, "infer")
                    url = target
                    continue

            redirection = Redirection(url)

            # NOTE: atomic_request will check for cancellation
            buffered_response = atomic_request(
                pool_manager,
                url,
                method=method,
                headers=headers,
                body=body,
                timeout=timeout,
                final_time=final_time,
                cancel_event=cancel_event,
            )

            redirection.status = buffered_response.status
            url_stack[url] = redirection

            # Attempting to find next location
            location = None

            if buffered_response.status not in REDIRECT_STATUSES:
                if buffered_response.status < 400:
                    # Refresh header
                    if follow_refresh_header:
                        refresh = buffered_response.getheader("refresh")

                        if refresh is not None:
                            p = parse_http_refresh(refresh)

                            if p is not None:
                                location = p[1]
                                redirection.type = "refresh-header"

                    # Reading a small chunk of the html
                    if location is None and (
                        follow_meta_refresh or follow_js_relocation
                    ):
                        buffered_response.prebuffer_up_to(CONTENT_PREBUFFER_UP_TO)

                    # Meta refresh
                    if location is None and follow_meta_refresh:
                        meta_refresh = find_meta_refresh(buffered_response.body)

                        if meta_refresh is not None:
                            location = meta_refresh[1]
                            redirection.type = "meta-refresh"

                    # JavaScript relocation
                    if location is None and follow_js_relocation:
                        js_relocation = find_javascript_relocation(
                            buffered_response.body
                        )

                        if js_relocation is not None:
                            location = js_relocation
                            redirection.type = "js-relocation"

                # Found the end
                if location is None:
                    redirection.type = "hit"

                # Canonical url
                if redirection.type == "hit":
                    if canonicalize:
                        buffered_response.prebuffer_up_to(LARGE_CONTENT_PREBUFFER_UP_TO)

                        canonical = find_canonical_link(buffered_response.body)

                        if canonical is not None and canonical != url:
                            canonical = urljoin(url, canonical)
                            redirection = Redirection(canonical, "canonical")
                            url_stack[canonical] = redirection

                    # Breaking free of the retry loop because we have a hit
                    break

            else:
                redirection.type = "location-header"
                location = buffered_response.getheader("location")

            # Invalid redirection
            if not location:
                raise InvalidRedirectError("Redirection is invalid")

            # Location badly encoded?
            # NOTE: we don't really have a way to consume headers as raw bytes
            # which means we must rely on encoding duck-typing. I expect this
            # to fail in a complicated manner in a distant future.
            try:
                if not location.isascii():
                    byte_location = location.encode("latin1")
                    encoding = infer_encoding(byte_location)

                    if (
                        encoding is not None
                        and encoding != "iso-8859-1"
                        and encoding != "latin1"
                        and encoding != "ascii"
                    ):
                        location = byte_location.decode(encoding)
            except (UnicodeEncodeError, UnicodeDecodeError):
                raise BadlyEncodedLocationHeaderError(
                    "Location header has invalid encoding"
                )

            # Resolving next url
            next_url = urljoin(url, location.strip())

            # Self loop?
            if next_url == url:
                raise SelfRedirectError("Self redirection")

            # Go to next
            url = next_url

        # We reached max redirects
        else:
            raise MaxRedirectsError("Maximum number of redirects exceeded")

    # NOTE: using BaseException here to avoid leaks on e.g. KeyboardInterrupt
    except BaseException:
        # NOTE: here we must make sure to cleanup any still alive
        # buffered response to avoid leaks
        if buffered_response is not None:
            buffered_response.close()

        raise

    # Compiling the stack and returning the last buffered response, still alive
    compiled_stack = list(url_stack.values())

    assert buffered_response is not None

    return compiled_stack, buffered_response


def build_request_headers(
    headers: Optional[Dict[str, str]] = None,
    cookie: Optional[Union[str, Dict[str, str]]] = None,
    spoof_ua: bool = False,
    json_body: bool = False,
    urlencoded_body: bool = False,
):
    # Formatting headers
    final_headers = {}

    if spoof_ua:
        final_headers["User-Agent"] = DEFAULT_SPOOFED_UA

    if cookie:
        if not isinstance(cookie, str):
            cookie = dict_to_cookie_string(cookie)

        final_headers["Cookie"] = cookie

    if json_body:
        final_headers["Content-Type"] = "application/json"
    elif urlencoded_body:
        final_headers["Content-Type"] = "application/x-www-form-urlencoded"

    # Note: headers passed explicitly by users always win
    if headers is not None:
        final_headers.update(headers)

    return final_headers


class Response(object):
    """
    Class representing a finalized HTTP response.

    It wraps a urllib3.HTTPResponse as well as its raw body and exposes a
    variety of useful utilities that will be used downstream.

    This class is used by high-level function of this module and is expected
    to be found elsewhere.

    Note that it will lazily compute required items when asked for certain
    properties.
    """

    __slots__ = (
        "__response",
        "__stack",
        "__body",
        "__text",
        "__url",
        "__datetime_utc",
        "__is_text",
        "__encoding",
        "__ext",
        "__mimetype",
        "__has_guessed_extension",
        "__has_guessed_encoding",
        "__has_decoded_text",
    )

    __response: urllib3.HTTPResponse
    __stack: Optional[RedirectionStack]
    __body: bytes
    __text: Optional[str]
    __url: str
    __datetime_utc: datetime
    __is_text: Optional[bool]
    __encoding: Optional[str]
    __ext: Optional[str]
    __mimetype: Optional[str]

    __has_guessed_extension: bool
    __has_guessed_encoding: bool
    __has_decoded_text: bool

    def __init__(
        self,
        url: str,
        stack: Optional[RedirectionStack],
        response: urllib3.HTTPResponse,
        body: bytes,
        known_encoding: Optional[str] = None,
    ):
        self.__url = url
        self.__stack = stack
        self.__response = response
        self.__body = body
        self.__text = None
        self.__datetime_utc = datetime.utcnow()
        self.__is_text = None
        self.__encoding = known_encoding
        self.__ext = None
        self.__mimetype = None

        self.__has_guessed_extension = False
        self.__has_guessed_encoding = known_encoding is not None
        self.__has_decoded_text = False

    def __guess_extension(self) -> None:
        if self.__has_guessed_extension:
            return

        # Guessing mime type
        # TODO: validate mime type string?
        url = self.__url
        assert url is not None
        mimetype, _ = mimetypes.guess_type(url)

        response = self.__response

        if "Content-Type" in response.headers:
            content_type = response.headers["Content-Type"]
            parsed_header = cgi.parse_header(content_type)

            if parsed_header and parsed_header[0].strip():
                mimetype = parsed_header[0].strip()

                # Dropping charset info
                if "," in mimetype:
                    mimetype = mimetype.split(",", 1)[0]

        if mimetype is None and looks_like_html(self.__body):
            mimetype = "text/html"

        if mimetype is not None:
            ext = mimetypes.guess_extension(mimetype)

            if ext == ".htm":
                ext = ".html"
            elif ext == ".jpe":
                ext = ".jpg"

            self.__mimetype = mimetype
            self.__ext = ext

        if mimetype is not None:
            self.__is_text = not is_binary_mimetype(mimetype)

        self.__has_guessed_extension = True

    def __guess_encoding(self) -> None:
        if self.__has_guessed_encoding:
            return

        self.__guess_extension()

        if not self.__is_text:
            return

        self.__encoding = infer_encoding(self.__body)

        self.__has_guessed_encoding = True

    def __decode(self, errors: str = "replace") -> None:
        if self.__has_decoded_text:
            return

        self.__guess_extension()
        self.__guess_encoding()

        assert self.__is_text is not None

        if not self.__is_text:
            raise TypeError("response is binary and cannot be decoded")

        self.__text = self.__body.decode(self.__encoding or "utf-8", errors=errors)
        self.__has_decoded_text = True

    @property
    def url(self) -> str:
        return self.__url

    @property
    def start_url(self) -> str:
        return self.__url

    @property
    def end_url(self) -> str:
        if self.__stack is None:
            return self.__url
        return self.__stack[-1].url

    @property
    def headers(self):
        return self.__response.headers

    @property
    def stack(self) -> Optional[RedirectionStack]:
        return self.__stack

    @property
    def was_redirected(self) -> bool:
        return self.start_url != self.end_url

    @property
    def status(self) -> int:
        return self.__response.status

    @property
    def end_datetime(self) -> datetime:
        return self.__datetime_utc

    @property
    def ext(self) -> Optional[str]:
        self.__guess_extension()
        return self.__ext

    @property
    def mimetype(self) -> Optional[str]:
        self.__guess_extension()
        return self.__mimetype

    @property
    def is_text(self) -> bool:
        self.__guess_extension()
        return self.__is_text  # type: ignore # At that point we know it's a bool

    @property
    def is_binary(self) -> bool:
        return not self.is_text

    @property
    def could_be_html(self) -> bool:
        mime = self.mimetype
        return mime is not None and "/htm" in mime

    @property
    def is_html(self) -> bool:
        return self.is_text and looks_like_html(self.__body)

    @property
    def encoding(self) -> Optional[str]:
        self.__guess_encoding()
        return self.__encoding

    @property
    def likely_encoding(self) -> str:
        encoding = self.encoding

        if encoding is None:
            return "utf-8"

        return encoding

    @property
    def encoding_from_headers(self) -> Optional[str]:
        return infer_encoding_from_headers(self.__response)

    # TODO: add encoding_from_xml & possible_encodings when required

    @property
    def body(self) -> bytes:
        return self.__body

    def __len__(self) -> int:
        return len(self.__body)

    @property
    def human_size(self) -> str:
        return format_filesize(len(self.__body))

    def text(self) -> str:
        self.__decode()
        return self.__text  # type: ignore # If we don't raise, this IS a string

    def json(self):
        return json.loads(self.text())

    def soup(
        self,
        engine: str = "lxml",
        ignore_xhtml_warning=False,
        strainer: Optional[SoupStrainer] = None,
    ) -> WonderfulSoup:
        with suppress_xml_parsed_as_html_warnings(bypass=not ignore_xhtml_warning):
            return WonderfulSoup(self.text(), engine, parse_only=strainer)

    def __repr__(self) -> str:
        attr: List[Union[str, Tuple[str, Union[str, bool]]]] = ["status", "url"]

        if self.url != self.end_url:
            attr.append(("resolved", self.end_url))

        attr.extend([("size", self.human_size), "mimetype"])

        if self.is_text:
            attr.append("encoding")

        return format_repr(self, attr)


def request(
    url: str,
    pool_manager: urllib3.PoolManager = DEFAULT_POOL_MANAGER,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    cookie: Optional[Union[str, Dict[str, str]]] = None,
    spoof_ua: bool = True,
    follow_redirects: bool = True,
    max_redirects: int = 5,
    follow_refresh_header: bool = True,
    follow_meta_refresh: bool = False,
    follow_js_relocation: bool = False,
    infer_redirection: bool = False,
    canonicalize: bool = False,
    known_encoding: Optional[str] = None,
    timeout: Optional[AnyTimeout] = None,
    body: Optional[Union[str, bytes]] = None,
    json_body: Optional[Any] = None,
    urlencoded_body: Optional[Mapping[str, Union[str, int, float]]] = None,
    cancel_event: Optional[Event] = None,
    raise_on_statuses: Optional[Container[int]] = None,
) -> Response:
    # Formatting headers
    final_headers = build_request_headers(
        headers=headers,
        cookie=cookie,
        spoof_ua=spoof_ua,
        json_body=json_body is not None,
    )

    # Dealing with body
    if json_body is not None:
        body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
    elif urlencoded_body is not None:
        body = "&".join(
            "%s=%s" % (quote(str(k)), quote(str(v))) for k, v in urlencoded_body.items()
        )

    if isinstance(body, str):
        body = body.encode("utf-8")

    stack: Optional[RedirectionStack] = None

    if not follow_redirects:
        buffered_response = atomic_request(
            pool_manager,
            url,
            method,
            headers=final_headers,
            body=body,
            timeout=timeout,
            cancel_event=cancel_event,
        )
    else:
        stack, buffered_response = atomic_resolve(
            pool_manager,
            url,
            method,
            headers=final_headers,
            body=body,
            max_redirects=max_redirects,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation,
            infer_redirection=infer_redirection,
            canonicalize=canonicalize,
            timeout=timeout,
            cancel_event=cancel_event,
        )

    if raise_on_statuses is not None:
        if buffered_response.status in raise_on_statuses:
            buffered_response.close()
            raise InvalidStatusError(buffered_response.status)

    response, body = buffered_response.read_and_unwrap()

    return Response(url, stack, response, body, known_encoding=known_encoding)


def resolve(
    url: str,
    pool_manager: urllib3.PoolManager = DEFAULT_POOL_MANAGER,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    cookie: Optional[Union[str, Dict[str, str]]] = None,
    spoof_ua: bool = True,
    max_redirects: int = 5,
    follow_refresh_header: bool = True,
    follow_meta_refresh: bool = False,
    follow_js_relocation: bool = False,
    infer_redirection: bool = False,
    timeout: Optional[AnyTimeout] = None,
    canonicalize: bool = False,
    cancel_event: Optional[Event] = None,
    raise_on_statuses: Optional[Container[int]] = None,
) -> RedirectionStack:
    final_headers = build_request_headers(
        headers=headers, cookie=cookie, spoof_ua=spoof_ua
    )

    stack, buffered_response = atomic_resolve(
        pool_manager,
        url,
        method,
        headers=final_headers,
        max_redirects=max_redirects,
        follow_refresh_header=follow_refresh_header,
        follow_meta_refresh=follow_meta_refresh,
        follow_js_relocation=follow_js_relocation,
        infer_redirection=infer_redirection,
        timeout=timeout,
        canonicalize=canonicalize,
        cancel_event=cancel_event,
    )

    buffered_response.close()

    if raise_on_statuses is not None and stack:
        last = stack[-1]

        if last.status is not None and last.status in raise_on_statuses:
            raise InvalidStatusError(last.status)

    return stack


def request_jsonrpc(
    url: str,
    method: str,
    pool_manager: urllib3.PoolManager = DEFAULT_POOL_MANAGER,
    *args,
    **kwargs
) -> Response:
    params = []

    if len(args) > 0:
        params = args
    elif len(kwargs) > 0:
        params = kwargs

    return request(
        url,
        pool_manager=pool_manager,
        method="POST",
        json_body={"method": method, "params": params},
        known_encoding="utf-8",
    )


ONE_DAY = 24 * 60 * 60


class log_request_retryer_before_sleep:
    def __init__(
        self, epilog_builder: Optional[Callable[[RetryCallState], Optional[str]]] = None
    ):
        if epilog_builder is not None and not callable(epilog_builder):
            raise TypeError("epilog_builder should be None or callable")

        self.epilog_builder = epilog_builder

    def __call__(self, retry_state: RetryCallState) -> None:
        assert retry_state.outcome is not None

        if not retry_state.outcome.failed:
            raise NotImplementedError

        exception = retry_state.outcome.exception()

        sleepers_logger.warn(
            "request_retryer starts sleeping",
            extra={
                "source": "request_retryer",
                "from_thread": threading.current_thread()
                is not threading.main_thread(),
                "retry_state": retry_state,
                "exception": exception,
                "sleep_time": retry_state.next_action.sleep,
                "epilog": self.epilog_builder(retry_state)
                if self.epilog_builder is not None
                else None,
            },
        )


class request_retryer_custom_exponential_backoff(wait_base):
    def __init__(self, min: float = 10, max: float = ONE_DAY, exp_base=4) -> None:
        self.min = min
        self.max = max
        self.exp_base = exp_base

    def __call__(self, retry_state: RetryCallState) -> float:
        # NOTE: we add/subtract randomly up to 1/4 of expected sleep time
        jitter = 0.5 - random.random()

        try:
            exp = self.exp_base ** (retry_state.attempt_number - 1)
            result = self.min * exp
            result += result / 2 * jitter
        except OverflowError:
            result = self.max

        return max(0, min(result, self.max))


class RequestRetrying(Retrying):
    def __init__(
        self, *args, invalid_statuses: Optional[Container[int]] = None, **kwargs
    ):
        self._invalid_statuses = invalid_statuses
        super().__init__(*args, **kwargs)

    def __call__(self, fn, *args, **kwargs):
        if self._invalid_statuses is not None and fn in (request, resolve):
            kwargs["raise_on_statuses"] = self._invalid_statuses

        return super().__call__(fn, *args, **kwargs)


def create_request_retryer(
    min: float = 10,
    max: float = ONE_DAY,
    max_attempts: int = 9,
    before_sleep=noop,
    additional_exceptions=None,
    retry_on_timeout: bool = True,
    retry_on_statuses: Optional[Container[int]] = None,
    predicate: Optional[Callable[[BaseException], bool]] = None,
    epilog: Optional[Callable[[RetryCallState], Optional[str]]] = None,
    cancel_event: Optional[Event] = None,
):
    # By default we only retry network issues, such as Internet being cut off etc.
    retryable_exception_types = [
        # urllib3 errors
        urllib3_exceptions.ProtocolError,
        # urllib errors
        urllib.error.URLError,
        # Low-level socket connection errors
        ConnectionAbortedError,
        ConnectionRefusedError,
        ConnectionResetError,
    ]

    # We also usually include most timeout errors
    if retry_on_timeout:
        retryable_exception_types.extend(
            [FinalTimeoutError, urllib3_exceptions.TimeoutError]
        )

    if retry_on_statuses is not None:
        retryable_exception_types.append(InvalidStatusError)

    if additional_exceptions:
        for exc in additional_exceptions:
            retryable_exception_types.append(exc)

    retry_condition = retry_if_exception_type(
        exception_types=tuple(retryable_exception_types)
    )

    # By default we also retry subsets of new connection error
    def temporary_failure_predicate(exc: BaseException) -> bool:
        if not isinstance(exc, urllib3_exceptions.NewConnectionError):
            return False

        msg = str(exc).lower()

        if "errno -3" in msg or "temporary failure in name resolution" in msg:
            return True

        return False

    retry_condition |= retry_if_exception(temporary_failure_predicate)

    if retry_on_statuses is not None:

        def status_predicate(exc: BaseException) -> bool:
            if isinstance(exc, InvalidStatusError) and exc.status in retry_on_statuses:
                return True

            return False

        retry_condition |= retry_if_exception(status_predicate)

    if callable(predicate):
        retry_condition |= retry_if_exception(predicate)

    retrying_kwargs = {
        "reraise": True,
        "wait": request_retryer_custom_exponential_backoff(min=min, max=max),
        "retry": retry_condition,
        "stop": stop_after_attempt(max_attempts),
        "before_sleep": rcompose(
            log_request_retryer_before_sleep(epilog), before_sleep
        ),
    }

    # Cancellable sleep?
    if cancel_event is not None:
        if cancel_event.is_set():
            raise TypeError("cannot retry using an already set cancel_event")

        retrying_kwargs["sleep"] = sleep_using_event(cancel_event)
        retrying_kwargs["stop"] |= stop_when_event_set(cancel_event)
        retrying_kwargs["retry"] &= retry_if_exception(
            lambda _: not cancel_event.is_set()
        )

    return RequestRetrying(invalid_statuses=retry_on_statuses, **retrying_kwargs)


def retrying_method(attr="retryer"):
    def decorate(fn):
        @functools.wraps(fn)
        def decorated(self, *args, **kwargs):
            retryer = getattr(self, attr)

            if not isinstance(retryer, Retrying):
                raise ValueError

            return retryer(fn, self, *args, **kwargs)

        return decorated

    return decorate
