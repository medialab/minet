# =============================================================================
# Minet Web Utilities
# =============================================================================
#
# Miscellaneous web-related functions used throughout the library.
#
from typing import Optional, Tuple, Union, OrderedDict, List, Any, Dict

import re
import cgi
import certifi
import random
import browser_cookie3
import urllib3
import urllib.error
import ural
import json
import mimetypes
import functools
import charset_normalizer as chardet
from bs4 import BeautifulSoup
from datetime import datetime
from timeit import default_timer as timer
from io import BytesIO
from threading import Event
from urllib.parse import urljoin
from urllib3 import HTTPResponse
from urllib3.exceptions import HTTPError
from urllib3.util.ssl_ import create_urllib3_context
from urllib.request import Request
from ebbe import rcompose, noop
from tenacity import (
    Retrying,
    retry_if_exception_type,
    retry_if_exception,
    stop_after_attempt,
)
from tenacity.wait import wait_base

from minet.encodings import is_supported_encoding, normalize_encoding
from minet.loggers import sleepers_logger
from minet.utils import is_binary_mimetype
from minet.exceptions import (
    RedirectError,
    MaxRedirectsError,
    InfiniteRedirectsError,
    InvalidRedirectError,
    InvalidURLError,
    SelfRedirectError,
    CancelledRequestError,
    FinalTimeoutError,
)
from minet.constants import (
    DEFAULT_SPOOFED_UA,
    DEFAULT_SPOOFED_TLS_CIPHERS,
    DEFAULT_URLLIB3_TIMEOUT,
    COOKIE_BROWSERS,
)

mimetypes.init()

# Types
AnyTimeout = Union[float, urllib3.Timeout]

# Handy regexes
BINARY_BOM_RE = re.compile(rb"^\xef\xbb\xbf")
CHARSET_RE = re.compile(rb'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I)
PRAGMA_RE = re.compile(rb'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I)
XML_RE = re.compile(rb'^<\?xml.*?encoding=["\']*(.+?)["\'>]', flags=re.I)
NOSCRIPT_RE = re.compile(rb"<noscript[^>]*>.*</noscript[^>]*>", flags=re.I)
META_REFRESH_RE = re.compile(
    rb"""<meta\s+http-equiv=['"]?refresh['"]?\s+content=['"]?([^"']+)['">]?""",
    flags=re.I,
)
JAVASCRIPT_LOCATION_RE = re.compile(
    rb"""(?:window\.)?location(?:\s*=\s*|\.replace\(\s*)['"`](.*?)['"`]"""
)
ESCAPED_SLASH_RE = re.compile(rb"\\\/")
ASCII_RE = re.compile(r"^[ -~]*$")
HTML_RE = re.compile(
    rb"^<(?:html|head|body|title|meta|link|span|div|img|ul|ol|[ap!?])", flags=re.I
)
CANONICAL_LINK_RE = re.compile(
    rb'<link\s*[^>]*\s+rel=(?:"\s*canonical\s*"|canonical|\'\s*canonical\s*\')\s+[^>]*\s?/?>'
)
HREF_RE = re.compile(rb'href=(\"[^"]+|\'[^\']+|[^\s]+)>?\s?', flags=re.I)

# Constants
CHARSET_DETECTION_CONFIDENCE_THRESHOLD = 0.9
REDIRECT_STATUSES = set(HTTPResponse.REDIRECT_STATUSES)
CONTENT_PREBUFFER_UP_TO = 1024
STREAMING_CHUNK_SIZE = 2**12
LARGE_CONTENT_PREBUFFER_UP_TO = 2**16
EXPECTED_WEB_ERRORS = (HTTPError, RedirectError, InvalidURLError, FinalTimeoutError)

assert CONTENT_PREBUFFER_UP_TO < LARGE_CONTENT_PREBUFFER_UP_TO


# TODO: add a version that tallies the possibilities
# NOTE: utf-16 is handled differently to account for endianness
# NOTE: file starting with a BOM are inferred preferentially
# See: https://github.com/medialab/minet/issues/550
def guess_response_encoding(
    response: urllib3.HTTPResponse, body: bytes, is_xml=False, infer=False
) -> Optional[str]:
    """
    Function taking an urllib3 response object and attempting to guess its
    encoding.
    """
    content_type_header = response.getheader("content-type")

    suboptimal_charset = None

    has_bom = bool(BINARY_BOM_RE.match(body))

    if content_type_header is not None:
        parsed_header = cgi.parse_header(content_type_header)

        if len(parsed_header) > 1:
            charset = parsed_header[1].get("charset")

            if charset is not None:
                if (
                    is_supported_encoding(charset)
                    and normalize_encoding(charset) != "utf16"
                    and not has_bom
                ):
                    return charset.lower()
                else:
                    suboptimal_charset = charset

    chunk = body[:CONTENT_PREBUFFER_UP_TO]

    # Data is empty
    if not chunk.strip():
        return None

    # TODO: use re.search to go faster!
    if is_xml:
        matches = re.findall(CHARSET_RE, chunk)

        if len(matches) == 0:
            matches = re.findall(PRAGMA_RE, chunk)

        if len(matches) == 0:
            matches = re.findall(XML_RE, chunk)

        # NOTE: here we are returning the last one, but we could also use
        # frequency at the expense of performance
        if len(matches) != 0:
            charset = matches[-1].lower().decode()

            if (
                is_supported_encoding(charset)
                and normalize_encoding(charset) != "utf16"
                and not has_bom
            ):
                return charset
            else:
                suboptimal_charset = charset

    if infer:
        inferrence_result = chardet.detect(body)

        # Could not detect anything
        if not inferrence_result or inferrence_result.get("confidence") is None:
            return None

        if inferrence_result["confidence"] >= CHARSET_DETECTION_CONFIDENCE_THRESHOLD:
            return inferrence_result["encoding"].lower()

    return suboptimal_charset


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


class CookieResolver(object):
    def __init__(self, jar):
        self.jar = jar

    def __call__(self, url):
        req = Request(url)
        self.jar.add_cookie_header(req)

        return req.get_header("Cookie") or None


def grab_cookies(browser="firefox"):
    if browser not in COOKIE_BROWSERS:
        raise TypeError('minet.utils.grab_cookies: unknown "%s" browser.' % browser)

    try:
        return CookieResolver(getattr(browser_cookie3, browser)())
    except browser_cookie3.BrowserCookieError as e:
        raise e


def dict_to_cookie_string(d):
    return "; ".join("%s=%s" % r for r in d.items())


def create_pool_manager(
    proxy: Optional[str] = None,
    threads: Optional[int] = None,
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

    if threads is not None:

        # TODO: maxsize should increase with group_parallelism
        manager_kwargs["maxsize"] = 10
        manager_kwargs["num_pools"] = threads * 2

    manager_kwargs.update(kwargs)

    if spoof_tls_ciphers:
        manager_kwargs["ssl_context"] = create_urllib3_context(
            ciphers=DEFAULT_SPOOFED_TLS_CIPHERS
        )

    if proxy is not None:
        return urllib3.ProxyManager(proxy, **manager_kwargs)

    return urllib3.PoolManager(**manager_kwargs)


DEFAULT_POOL_MANAGER = create_pool_manager(maxsize=10, num_pools=10)


def stream_request_body(
    response: urllib3.HTTPResponse,
    body: BytesIO,
    chunk_size: int = STREAMING_CHUNK_SIZE,
    cancel_event: Optional[Event] = None,
    final_time: Optional[float] = None,
    up_to: Optional[int] = None,
) -> bool:
    if up_to is not None and body.tell() >= up_to:
        return False

    for data in response.stream(chunk_size):
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


class BufferedResponse(object):
    """
    Class wrapping a urllib3.HTTPResponse and representing a response whose
    body has not been yet fully read.

    It is a low-level representation used in the minet.web module that should
    not leak outside normally.

    It is able to stream a response's body safely all while keeping track of
    a "final" timeout correctly enforced to bypass python socket race condition
    issues on read loops and is also able to be cancelled if required.
    """

    __slots__ = (
        "__inner",
        "__body",
        "__cancel_event",
        "__final_time",
        "__finished",
        "__unwrapped",
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
        self.__unwrapped = False

    def __len__(self) -> int:
        return self.__body.getbuffer().nbytes

    def __stream(
        self, chunk_size: int = STREAMING_CHUNK_SIZE, up_to: Optional[int] = None
    ) -> None:
        if self.__unwrapped:
            raise TypeError("buffered response was already unwrapped")

        if self.__finished:
            return

        fully_read = False

        try:
            fully_read = stream_request_body(
                self.__inner,
                chunk_size=chunk_size,
                cancel_event=self.__cancel_event,
                final_time=self.__final_time,
                body=self.__body,
                up_to=up_to,
            )
        finally:
            if fully_read:
                self.__finished = fully_read
                self.close()

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
        # NOTE: releasing and closing is a noop if already done
        self.__inner.release_conn()
        self.__inner.close()

    def unwrap(self) -> Tuple[urllib3.HTTPResponse, bytes]:
        self.__unwrapped = True
        self.close()
        return self.__inner, self.__body.getvalue()

    def read(self, chunk_size: int = STREAMING_CHUNK_SIZE) -> None:
        self.__stream(chunk_size=chunk_size)

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
        raise InvalidURLError(url=url)

    # Performing request
    request_kwargs = {
        "headers": headers,
        "body": body,
        "preload_content": False,
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


class Redirection(object):
    __slots__ = ("status", "type", "url")

    def __init__(self, url: str, _type="hit"):
        self.status: Optional[int] = None
        self.url: str = url
        self.type: str = _type

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
    error: Optional[Exception] = None
    buffered_response: Optional[BufferedResponse] = None

    if final_time is None:
        final_time = pool_manager_aware_timeout_to_final_time(pool_manager, timeout)

    for _ in range(max_redirects):
        if infer_redirection:
            target = ural.infer_redirection(url, recursive=False)

            if target != url:
                url_stack[url] = Redirection(url, "infer")
                url = target
                continue

        # We close last buffered_response as it won't be used anymore
        if buffered_response:
            buffered_response.close()

        redirection = Redirection(url)

        try:
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

        # Request error
        except HTTPError as e:
            url_stack[url] = redirection
            error = e
            break

        # Cycle
        if url in url_stack:
            error = InfiniteRedirectsError("Infinite redirects")
            break

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
                if location is None and (follow_meta_refresh or follow_js_relocation):
                    try:
                        buffered_response.prebuffer_up_to(CONTENT_PREBUFFER_UP_TO)
                    except Exception as e:
                        error = e
                        break

                # Meta refresh
                if location is None and follow_meta_refresh:
                    meta_refresh = find_meta_refresh(buffered_response.body)

                    if meta_refresh is not None:
                        location = meta_refresh[1]
                        redirection.type = "meta-refresh"

                # JavaScript relocation
                if location is None and follow_js_relocation:
                    js_relocation = find_javascript_relocation(buffered_response.body)

                    if js_relocation is not None:
                        location = js_relocation
                        redirection.type = "js-relocation"

            # Found the end
            if location is None:
                redirection.type = "hit"

            # Canonical url
            if redirection.type == "hit":
                if canonicalize:
                    try:
                        buffered_response.prebuffer_up_to(LARGE_CONTENT_PREBUFFER_UP_TO)
                    except Exception as e:
                        error = e
                        break

                    canonical = find_canonical_link(buffered_response.body)

                    if canonical is not None and canonical != url:
                        canonical = urljoin(url, canonical)
                        redirection = Redirection(canonical, "canonical")
                        url_stack[canonical] = redirection

                break

        else:
            redirection.type = "location-header"
            location = buffered_response.getheader("location")

        # Invalid redirection
        if not location:
            error = InvalidRedirectError("Redirection is invalid")
            break

        # Location badly encoded?
        try:
            if not ASCII_RE.match(location):
                byte_location = location.encode("latin1")
                detection = chardet.detect(byte_location)
                guessed_encoding = detection["encoding"].lower()

                if (
                    guessed_encoding != "iso-8859-1"
                    and guessed_encoding != "ascii"
                    and detection["confidence"]
                    >= CHARSET_DETECTION_CONFIDENCE_THRESHOLD
                ):
                    location = byte_location.decode(guessed_encoding)
        except Exception:
            pass

        # Resolving next url
        next_url = urljoin(url, location.strip())

        # Self loop?
        if next_url == url:
            error = SelfRedirectError("Self redirection")
            break

        # Go to next
        url = next_url

    # We reached max redirects
    else:
        error = MaxRedirectsError("Maximum number of redirects exceeded")

    # NOTE: error is raised that late to be sure we cleanup resources attached
    # to the connection
    if error is not None:
        if buffered_response is not None:
            buffered_response.close()
        raise error

    compiled_stack = list(url_stack.values())

    assert buffered_response is not None

    return compiled_stack, buffered_response


def build_request_headers(headers=None, cookie=None, spoof_ua=False, json_body=False):

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

    It also works as a kind of dict that can bring around meta information.
    """

    __slots__ = (
        "__response",
        "__stack",
        "__body",
        "__text",
        "__url",
        "__meta",
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
    __meta: Dict[str, Any]
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
        self.__meta = {}
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

        self.__encoding = guess_response_encoding(
            self.__response, self.__body, is_xml=True, infer=True
        )

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
    def body(self) -> bytes:
        return self.__body

    def text(self) -> str:
        self.__decode()
        return self.__text  # type: ignore # If we don't raise, this IS a string

    def json(self):
        return json.loads(self.text())

    def soup(self, engine: str = "lxml") -> BeautifulSoup:
        return BeautifulSoup(self.text(), engine)

    def __getitem__(self, name: str) -> Any:
        return self.__meta[name]

    def __setitem__(self, name: str, value: Any) -> None:
        self.__meta[name] = value

    def __contains__(self, name: str) -> bool:
        return name in self.__meta

    def get(self, name: str, default=None) -> Optional[Any]:
        return self.__meta.get(name, default)

    def set(self, name: str, value: Any) -> None:
        self.__meta[name] = value


def request(
    url: str,
    pool_manager: urllib3.PoolManager = DEFAULT_POOL_MANAGER,
    method: str = "GET",
    headers=None,
    cookie=None,
    spoof_ua: bool = True,
    follow_redirects: bool = True,
    max_redirects: int = 5,
    follow_refresh_header: bool = True,
    follow_meta_refresh: bool = False,
    follow_js_relocation: bool = False,
    canonicalize: bool = False,
    known_encoding: Optional[str] = None,
    timeout: Optional[AnyTimeout] = None,
    body=None,
    json_body=None,
    cancel_event: Optional[Event] = None,
) -> Response:

    # Formatting headers
    final_headers = build_request_headers(
        headers=headers,
        cookie=cookie,
        spoof_ua=spoof_ua,
        json_body=json_body is not None,
    )

    # Dealing with body
    final_body = None

    if isinstance(body, bytes):
        final_body = body
    elif isinstance(body, str):
        final_body = body.encode("utf-8")

    if json_body is not None:
        final_body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")

    stack: Optional[RedirectionStack] = None

    if not follow_redirects:
        buffered_response = atomic_request(
            pool_manager,
            url,
            method,
            headers=final_headers,
            body=final_body,
            timeout=timeout,
            cancel_event=cancel_event,
        )
    else:
        stack, buffered_response = atomic_resolve(
            pool_manager,
            url,
            method,
            headers=final_headers,
            body=final_body,
            max_redirects=max_redirects,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation,
            canonicalize=canonicalize,
            timeout=timeout,
            cancel_event=cancel_event,
        )

    buffered_response.read()
    response, body = buffered_response.unwrap()

    return Response(url, stack, response, body, known_encoding=known_encoding)


def resolve(
    url: str,
    pool_manager: urllib3.PoolManager = DEFAULT_POOL_MANAGER,
    method: str = "GET",
    headers=None,
    cookie=None,
    spoof_ua: bool = True,
    max_redirects: int = 5,
    follow_refresh_header: bool = True,
    follow_meta_refresh: bool = False,
    follow_js_relocation: bool = False,
    infer_redirection: bool = False,
    timeout: Optional[AnyTimeout] = None,
    canonicalize: bool = False,
    cancel_event: Optional[Event] = None,
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


def log_request_retryer_before_sleep(retry_state):
    if not retry_state.outcome.failed:
        raise NotImplementedError

    exception = retry_state.outcome.exception()

    sleepers_logger.warn(
        "request_retryer starts sleeping",
        extra={
            "source": "request_retryer",
            "retry_state": retry_state,
            "exception": exception,
            "sleep_time": retry_state.next_action.sleep,
        },
    )


class request_retryer_custom_exponential_backoff(wait_base):
    def __init__(self, min=10, max=ONE_DAY, exp_base=4) -> None:
        self.min = min
        self.max = max
        self.exp_base = exp_base

    def __call__(self, retry_state):
        # NOTE: we add/subtract randomly up to 1/4 of expected sleep time
        jitter = 0.5 - random.random()

        try:
            exp = self.exp_base ** (retry_state.attempt_number - 1)
            result = self.min * exp
            result += result / 2 * jitter
        except OverflowError:
            result = self.max

        return max(0, min(result, self.max))


def create_request_retryer(
    min: float = 10,
    max: float = ONE_DAY,
    max_attempts: int = 9,
    before_sleep=noop,
    additional_exceptions=None,
    predicate=None,
):
    global GLOBAL_RETRYER_BEFORE_SLEEP

    retryable_exception_types = [
        FinalTimeoutError,
        urllib3.exceptions.TimeoutError,
        urllib3.exceptions.ProtocolError,
        urllib.error.URLError,
    ]

    if additional_exceptions:
        for exc in additional_exceptions:
            retryable_exception_types.append(exc)

    retry_condition = retry_if_exception_type(
        exception_types=tuple(retryable_exception_types)
    )

    if callable(predicate):
        retry_condition |= retry_if_exception(predicate)

    return Retrying(
        wait=request_retryer_custom_exponential_backoff(min=min, max=max),
        retry=retry_condition,
        stop=stop_after_attempt(max_attempts),
        before_sleep=rcompose(log_request_retryer_before_sleep, before_sleep),
    )


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
