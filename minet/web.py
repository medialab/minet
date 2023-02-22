# =============================================================================
# Minet Web Utilities
# =============================================================================
#
# Miscellaneous web-related functions used throughout the library.
#
from typing import Optional, Tuple

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
from datetime import datetime
from timeit import default_timer as timer
from io import BytesIO
from threading import Event
from collections import OrderedDict
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

# Handy regexes
BINARY_BOM_RE = re.compile(rb"\xef\xbb\xbf")
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
EXPECTED_WEB_ERRORS = (HTTPError, RedirectError, InvalidURLError)

assert CONTENT_PREBUFFER_UP_TO < LARGE_CONTENT_PREBUFFER_UP_TO


def prebuffer_response_up_to(response, target):
    try:
        if response._body is None:
            response._body = response.read(target)
        else:
            target -= len(response._body)

            if target <= 0:
                return None

            response._body += response.read(target)

    except Exception as e:
        return e

    return None


# TODO: add a version that tallies the possibilities
# NOTE: utf-16 is handled differently to account for endianness
# NOTE: file starting with a BOM are inferred preferentially
# See: https://github.com/medialab/minet/issues/550
def guess_response_encoding(response, is_xml=False, infer=False):
    """
    Function taking an urllib3 response object and attempting to guess its
    encoding.
    """
    content_type_header = response.getheader("content-type")

    suboptimal_charset = None

    # TODO: think about prebuffering
    data = response.data

    has_bom = bool(BINARY_BOM_RE.match(data[:10]))

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

    chunk = data[:CONTENT_PREBUFFER_UP_TO]

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
        inferrence_result = chardet.detect(data)

        # Could not detect anything
        if not inferrence_result or inferrence_result.get("confidence") is None:
            return None

        if inferrence_result["confidence"] >= CHARSET_DETECTION_CONFIDENCE_THRESHOLD:
            return inferrence_result["encoding"].lower()

    return suboptimal_charset


def looks_like_html(html_chunk):
    return HTML_RE.match(html_chunk) is not None


def parse_http_header(header):
    key, value = header.split(":", 1)

    return key.strip(), value.strip()


# TODO: take more cases into account...
#   http://www.otsukare.info/2015/03/26/refresh-http-header
def parse_http_refresh(value):
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


def find_canonical_link(html_chunk):
    m = CANONICAL_LINK_RE.search(html_chunk)

    if not m:
        return None

    return extract_href(m.group())


def find_meta_refresh(html_chunk):
    m = META_REFRESH_RE.search(html_chunk)

    if not m:
        return None

    return parse_http_refresh(m.group(1))


def find_javascript_relocation(html_chunk):
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


def create_pool(
    proxy=None, threads=None, insecure=False, spoof_tls_ciphers=False, **kwargs
):
    """
    Helper function returning a urllib3 pool manager with sane defaults.
    """

    manager_kwargs = {"timeout": DEFAULT_URLLIB3_TIMEOUT}

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


DEFAULT_POOL = create_pool(maxsize=10, num_pools=10)


def stream_request_body(
    response: urllib3.HTTPResponse,
    body: BytesIO,
    chunk_size: int = STREAMING_CHUNK_SIZE,
    cancel_event: Optional[Event] = None,
    end_time: Optional[float] = None,
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

        if end_time is not None:
            if timer() >= end_time:
                raise FinalTimeoutError

    # This is the only place we know the body has been fully read
    return True


class BufferedResponse(object):
    __slots__ = ("__inner", "__body", "__cancel_event", "__end_time", "__finished")

    def __init__(
        self,
        response: urllib3.HTTPResponse,
        cancel_event: Optional[Event],
        end_time: Optional[float] = None,
    ):
        self.__inner = response
        self.__cancel_event = cancel_event
        self.__end_time = end_time
        self.__body = BytesIO()
        self.__finished = False

    def __len__(self) -> int:
        return self.__body.getbuffer().nbytes

    def __stream(
        self, chunk_size: int = STREAMING_CHUNK_SIZE, up_to: Optional[int] = None
    ):
        if self.__finished:
            return

        fully_read = False

        try:
            stream_request_body(
                self.__inner,
                chunk_size=chunk_size,
                cancel_event=self.__cancel_event,
                end_time=self.__end_time,
                body=self.__body,
                up_to=up_to,
            )
        finally:
            if fully_read:
                self.__finished = fully_read
                self.close()

    def close(self) -> None:
        # NOTE: releasing and closing is a noop if already done
        self.__inner.release_conn()
        self.__inner.close()

    def unwrap(self) -> Tuple[urllib3.HTTPResponse, bytes]:
        self.read()
        return self.__inner, self.__body.getvalue()

    def read(self, chunk_size: int = STREAMING_CHUNK_SIZE) -> None:
        self.__stream(chunk_size=chunk_size)

    def prebuffer_up_to(
        self, amount: int, chunk_size: int = STREAMING_CHUNK_SIZE
    ) -> None:
        self.__stream(chunk_size=chunk_size, up_to=amount)


def make_request(
    pool,
    url: str,
    method="GET",
    headers=None,
    preload_content=True,
    release_conn=True,
    timeout=None,
    body=None,
):
    """
    Generic request helpers using a urllib3 pool to access some resource.
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
        "preload_content": preload_content,
        "release_conn": release_conn,
        "redirect": False,
        "retries": False,
    }

    if timeout is not None:
        request_kwargs["timeout"] = timeout

    return pool.request(method, url, **request_kwargs)


class Redirection(object):
    __slots__ = ("status", "type", "url")

    def __init__(self, url, _type="hit"):
        self.status = None
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


def make_resolve(
    pool,
    url,
    method="GET",
    headers=None,
    max_redirects=5,
    follow_refresh_header=True,
    follow_meta_refresh=False,
    follow_js_relocation=False,
    return_response=False,
    infer_redirection=False,
    timeout=None,
    body=None,
    canonicalize=False,
):
    """
    Helper function attempting to resolve the given url.
    """

    url_stack = OrderedDict()
    error = None
    response = None

    for _ in range(max_redirects):
        if infer_redirection:
            target = ural.infer_redirection(url, recursive=False)

            if target != url:
                url_stack[url] = Redirection(url, "infer")
                url = target
                continue

        if response:
            response.release_conn()
            response.close()

        redirection = Redirection(url)

        try:
            response = make_request(
                pool,
                url,
                method=method,
                headers=headers,
                body=body,
                preload_content=False,
                release_conn=False,
                timeout=timeout,
            )

        # Request error
        except HTTPError as e:
            redirection.type = "error"
            url_stack[url] = redirection
            error = e
            break

        # Cycle
        if url in url_stack:
            error = InfiniteRedirectsError("Infinite redirects")
            break

        redirection.status = response.status
        url_stack[url] = redirection
        location = None

        if response.status not in REDIRECT_STATUSES:

            if response.status < 400:

                if follow_refresh_header:
                    refresh = response.getheader("refresh")

                    if refresh is not None:
                        p = parse_http_refresh(refresh)

                        if p is not None:
                            location = p[1]
                            redirection.type = "refresh-header"

                # Reading a small chunk of the html
                if location is None and (follow_meta_refresh or follow_js_relocation):
                    prebuffer_error = prebuffer_response_up_to(
                        response, CONTENT_PREBUFFER_UP_TO
                    )

                    if prebuffer_error is not None:
                        redirection.type = "error"
                        break

                # Meta refresh
                if location is None and follow_meta_refresh:
                    meta_refresh = find_meta_refresh(response._body)

                    if meta_refresh is not None:
                        location = meta_refresh[1]
                        redirection.type = "meta-refresh"

                # JavaScript relocation
                if location is None and follow_js_relocation:
                    js_relocation = find_javascript_relocation(response._body)

                    if js_relocation is not None:
                        location = js_relocation
                        redirection.type = "js-relocation"

            # Found the end
            if location is None:
                redirection.type = "hit"

            # Canonical url
            if redirection.type == "hit":
                if canonicalize:
                    prebuffer_error = prebuffer_response_up_to(
                        response, LARGE_CONTENT_PREBUFFER_UP_TO
                    )

                    if prebuffer_error is not None:
                        redirection.type = "error"
                        break

                    canonical = find_canonical_link(response._body)

                    if canonical is not None and canonical != url:
                        canonical = urljoin(url, canonical)
                        redirection = Redirection(canonical, "canonical")
                        url_stack[canonical] = redirection

                break

        else:
            redirection.type = "location-header"
            location = response.getheader("location")

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

    # Cleanup
    if response and not return_response:
        response.release_conn()
        response.close()

    # NOTE: error is raised that late to be sure we cleanup resources attached
    # to the connection
    if error is not None:
        raise error

    compiled_stack = list(url_stack.values())

    if return_response:
        return compiled_stack, response

    return compiled_stack


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


def request(
    url,
    pool=DEFAULT_POOL,
    method="GET",
    headers=None,
    cookie=None,
    spoof_ua=True,
    follow_redirects=True,
    max_redirects=5,
    follow_refresh_header=True,
    follow_meta_refresh=False,
    follow_js_relocation=False,
    timeout=None,
    body=None,
    json_body=None,
):

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

    if not follow_redirects:
        return make_request(
            pool, url, method, headers=final_headers, body=final_body, timeout=timeout
        )
    else:
        _, response = make_resolve(
            pool,
            url,
            method,
            headers=final_headers,
            body=final_body,
            max_redirects=max_redirects,
            return_response=True,
            follow_refresh_header=follow_refresh_header,
            follow_meta_refresh=follow_meta_refresh,
            follow_js_relocation=follow_js_relocation,
            timeout=timeout,
        )

        # Finishing reading body
        try:
            response._body = (response._body or b"") + response.read()
        finally:
            if response is not None:
                response.close()
                response.release_conn()

        return response


def resolve(
    url,
    pool=DEFAULT_POOL,
    method="GET",
    headers=None,
    cookie=None,
    spoof_ua=True,
    max_redirects=5,
    follow_refresh_header=True,
    follow_meta_refresh=False,
    follow_js_relocation=False,
    infer_redirection=False,
    timeout=None,
    canonicalize=False,
):

    final_headers = build_request_headers(
        headers=headers, cookie=cookie, spoof_ua=spoof_ua
    )

    return make_resolve(
        pool,
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
    )


def extract_response_meta(response, guess_encoding=True, guess_extension=True):
    meta = {
        "ext": None,
        "mimetype": None,
        "encoding": None,
        "is_text": None,
        "datetime_utc": None,
    }

    # Marking time at which the fetch result object was created
    meta["datetime_utc"] = datetime.utcnow()

    # Guessing extension
    if guess_extension:

        # Guessing mime type
        # TODO: validate mime type string?
        mimetype, _ = mimetypes.guess_type(response.geturl())

        if "Content-Type" in response.headers:
            content_type = response.headers["Content-Type"]
            parsed_header = cgi.parse_header(content_type)

            if parsed_header and parsed_header[0].strip():
                mimetype = parsed_header[0].strip()

        if mimetype is None and looks_like_html(
            response.data[:CONTENT_PREBUFFER_UP_TO]
        ):
            mimetype = "text/html"

        if mimetype is not None:
            ext = mimetypes.guess_extension(mimetype)

            if ext == ".htm":
                ext = ".html"
            elif ext == ".jpe":
                ext = ".jpg"

            meta["mimetype"] = mimetype
            meta["ext"] = ext

    if meta["mimetype"] is not None:
        meta["is_text"] = not is_binary_mimetype(meta["mimetype"])

        if not meta["is_text"]:
            guess_encoding = False

    # Guessing encoding
    if guess_encoding:
        meta["encoding"] = guess_response_encoding(response, is_xml=True, infer=True)

    return meta


def request_jsonrpc(url, method, pool=DEFAULT_POOL, *args, **kwargs):
    params = []

    if len(args) > 0:
        params = args
    elif len(kwargs) > 0:
        params = kwargs

    response = request(
        url, pool=pool, method="POST", json_body={"method": method, "params": params}
    )

    data = json.loads(response.data)

    return response, data


def request_json(url, pool=DEFAULT_POOL, *args, **kwargs):
    response = request(url, pool=pool, *args, **kwargs)

    return response, json.loads(response.data.decode())


def request_text(url, pool=DEFAULT_POOL, *args, encoding="utf-8", **kwargs):
    response = request(url, pool=pool, *args, **kwargs)
    return response, response.data.decode(encoding)


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
    min=10,
    max=ONE_DAY,
    max_attempts=9,
    before_sleep=noop,
    additional_exceptions=None,
    predicate=None,
):
    global GLOBAL_RETRYER_BEFORE_SLEEP

    retryable_exception_types = [
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
