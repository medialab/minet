from typing import Optional, Dict, List, Union
from minet.types import AnyTimeout, RedirectionStack, Redirection, HTTPHeaderDict

import pycurl
import certifi
from dataclasses import dataclass
from ebbe import format_repr, format_filesize
from threading import Event
from ural import is_url
from urllib3 import Timeout
from urllib.parse import urljoin
from urllib3.util.url import parse_url

from minet.constants import REDIRECT_STATUSES
from minet.exceptions import (
    CancelledRequestError,
    MaxRedirectsError,
    InvalidURLError,
    PycurlError,
    PycurlHostResolutionError,
    PycurlTimeoutError,
    PycurlConnectionRefusedError,
    PycurlSSLError,
    PycurlReceiveError,
    PycurlSendError,
)

pycurl.global_init(pycurl.GLOBAL_ALL)

SHARE = pycurl.CurlShare()
SHARE.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)
SHARE.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_SSL_SESSION)
SHARE.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_CONNECT)

CURL_HANDLE_POOL: List[pycurl.Curl] = []


@dataclass
class PycurlResult:
    url: str
    body: bytes
    headers: HTTPHeaderDict
    status: int
    stack: RedirectionStack

    def __repr__(self) -> str:
        return format_repr(
            self, ["url", "status", ("size", format_filesize(len(self.body)))]
        )


def sanitize_url(url: str) -> str:
    return parse_url(url).url


def coerce_error(
    error: pycurl.error,
) -> Union[PycurlError, CancelledRequestError, MaxRedirectsError]:
    code = error.args[0]

    if code == pycurl.E_ABORTED_BY_CALLBACK:
        return CancelledRequestError()

    if code == pycurl.E_TOO_MANY_REDIRECTS:
        return MaxRedirectsError()

    if code == pycurl.E_OPERATION_TIMEDOUT:
        return PycurlTimeoutError(error)

    if code == pycurl.E_COULDNT_RESOLVE_HOST:
        return PycurlHostResolutionError(error)

    if code == pycurl.E_COULDNT_CONNECT:
        return PycurlConnectionRefusedError(error)

    if code in (
        pycurl.E_SSL_CACERT,
        pycurl.E_PEER_FAILED_VERIFICATION,
        pycurl.E_SSL_CONNECT_ERROR,
        pycurl.E_SSL_CERTPROBLEM,
        pycurl.E_SSL_CIPHER,
    ):
        return PycurlSSLError(error)

    if code == pycurl.E_RECV_ERROR:
        return PycurlReceiveError(error)

    if code == pycurl.E_SEND_ERROR:
        return PycurlSendError(error)

    return PycurlError(error)


def setup_curl_handle(
    curl: pycurl.Curl,
    url: str,
    response_headers: HTTPHeaderDict,
    stack: RedirectionStack,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    follow_redirects: bool = True,
    max_redirects: int = 5,
    compressed: bool = False,
    timeout: Optional[AnyTimeout] = None,
    cancel_event: Optional[Event] = None,
    verbose: bool = False,
) -> None:
    # Basics
    curl.setopt(pycurl.URL, sanitize_url(url))
    curl.setopt(pycurl.CAINFO, certifi.where())

    # NOTE: this is important for multithreading
    curl.setopt(pycurl.NOSIGNAL, True)

    if verbose:
        curl.setopt(pycurl.VERBOSE, True)

    if compressed:
        curl.setopt(pycurl.ACCEPT_ENCODING, "")

    # Method
    method = method.upper()

    if method == "GET":
        curl.setopt(pycurl.HTTPGET, True)
    elif method == "HEAD":
        curl.setopt(pycurl.NOBODY, True)
    elif method == "POST":
        curl.setopt(pycurl.POST, True)
    elif method == "PUT":
        curl.setopt(pycurl.PUT, True)
    else:
        curl.setopt(pycurl.CUSTOMREQUEST, method)

    # Timeout
    if timeout is not None:
        if isinstance(timeout, Timeout):
            total_timeout = None

            if timeout.total is not None:
                total_timeout = timeout.total
            else:
                if timeout.read_timeout is not None:
                    total_timeout = timeout.read_timeout
                if timeout.connect_timeout is not None:
                    if total_timeout is not None:
                        total_timeout += timeout.connect_timeout
                    else:
                        total_timeout = timeout.connect_timeout

            if total_timeout is not None:
                curl.setopt(pycurl.TIMEOUT_MS, int(total_timeout * 1000))

            if timeout.connect_timeout is not None:
                curl.setopt(
                    pycurl.CONNECTTIMEOUT_MS, int(timeout.connect_timeout * 1000)
                )

        else:
            curl.setopt(pycurl.TIMEOUT_MS, int(timeout * 1000))

    # Writing headers
    curl_headers = []

    if headers is not None:
        for n, v in headers.items():
            curl_headers.append(b"%s: %s" % (n.encode("ascii"), v.encode("latin1")))

    # NOTE: we must override Expect and Pragma to avoid unwanted libcurl magic
    if headers is None or "Expect" not in headers:
        curl_headers.append(b"Expect:")

    if headers is None or "Pragma" not in headers:
        curl_headers.append(b"Pragma:")

    curl.setopt(pycurl.HTTPHEADER, curl_headers)

    # Reading headers
    current_url = url
    expecting_location_with_status: Optional[int] = None

    def header_function(header_line):
        nonlocal current_url
        nonlocal expecting_location_with_status

        header_line = header_line.rstrip()
        header_line = header_line.decode("iso-8859-1")

        # Detecting new call, resetting headers
        if header_line.startswith("HTTP/"):
            response_headers.clear()

            status = int(header_line.split(" ", 1)[1][:3])

            if status in REDIRECT_STATUSES:
                expecting_location_with_status = status

            return

        if ":" not in header_line:
            return

        name, value = header_line.split(":", 1)

        name = name.strip()
        value = value.strip()

        if expecting_location_with_status is not None and name.lower() == "location":
            stack.append(
                Redirection(
                    current_url,
                    "location-header",
                    status=expecting_location_with_status,
                )
            )
            next_url = urljoin(current_url, value).strip()
            current_url = next_url
            expecting_location_with_status = None

        response_headers[name] = value

    curl.setopt(pycurl.HEADERFUNCTION, header_function)

    # Redirections
    if follow_redirects:
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.MAXREDIRS, max_redirects)

    # Cancellation
    if cancel_event is not None:
        curl.setopt(pycurl.NOPROGRESS, False)

        def progress_function(
            download_total, downloaded_total, upload_total, uploaded_total
        ) -> int:
            if cancel_event.is_set():
                return 1

            return 0

        curl.setopt(pycurl.XFERINFOFUNCTION, progress_function)


# TODO: body
# TODO: invalid status error (pycurl has a way I think)?
# TODO: error serialization, error retrying conversion
# TODO: pool of curl handles with multi (tricks from https://github.com/tornadoweb/tornado/blob/master/tornado/curl_httpclient.py)
def request_with_pycurl(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    follow_redirects: bool = True,
    max_redirects: int = 5,
    compressed: bool = False,
    timeout: Optional[AnyTimeout] = None,
    cancel_event: Optional[Event] = None,
    verbose: bool = False,
) -> PycurlResult:
    # Preemptive cancellation
    if cancel_event is not None and cancel_event.is_set():
        raise CancelledRequestError

    if not is_url(
        url, require_protocol=True, tld_aware=True, allow_spaces_in_path=True
    ):
        raise InvalidURLError(url)

    try:
        curl = CURL_HANDLE_POOL.pop()
        curl.reset()
    except IndexError:
        curl = pycurl.Curl()
        curl.setopt(pycurl.SHARE, SHARE)

    response_headers = HTTPHeaderDict()
    stack = []

    setup_curl_handle(
        curl,
        url=url,
        response_headers=response_headers,
        stack=stack,
        method=method,
        headers=headers,
        follow_redirects=follow_redirects,
        max_redirects=max_redirects,
        compressed=compressed,
        timeout=timeout,
        cancel_event=cancel_event,
        verbose=verbose,
    )

    # Performing
    try:
        body = curl.perform_rb()
    except pycurl.error as error:
        CURL_HANDLE_POOL.append(curl)

        raise coerce_error(error)

    status = curl.getinfo(pycurl.HTTP_CODE)
    effective_url = curl.getinfo(pycurl.EFFECTIVE_URL)
    CURL_HANDLE_POOL.append(curl)

    stack.append(Redirection(effective_url, status=status))

    return PycurlResult(
        url=url,
        body=body,
        headers=response_headers,
        status=status,
        stack=stack,
    )
