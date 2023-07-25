from typing import Optional, Dict
from minet.types import AnyTimeout

import pycurl
import certifi
from io import BytesIO
from dataclasses import dataclass
from ebbe import format_repr, format_filesize
from threading import Event
from urllib3 import Timeout

from minet.exceptions import CancelledRequestError

try:
    from urllib3 import HTTPHeaderDict
except ImportError:
    from urllib3._collections import HTTPHeaderDict


@dataclass
class PycurlResult:
    url: str
    body: bytes
    headers: HTTPHeaderDict
    status: int

    def __repr__(self) -> str:
        return format_repr(
            self, ["url", "status", ("size", format_filesize(len(self.body)))]
        )


# TODO: redirection stack (or handle it from minet.web?)
# TODO: reset headers on redirection
# TODO: body
# TODO: set headers
# TODO: decompress?
# TODO: error serialization, error retrying conversion
# TODO: pool of curl handles with multi (tricks from https://github.com/tornadoweb/tornado/blob/master/tornado/curl_httpclient.py)
def request_with_pycurl(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    follow_redirects: bool = True,
    max_redirects: int = 5,
    timeout: Optional[AnyTimeout] = None,
    cancel_event: Optional[Event] = None,
    verbose: bool = False,
) -> PycurlResult:
    # Preemptive cancellation
    if cancel_event is not None and cancel_event.is_set():
        raise CancelledRequestError

    curl = pycurl.Curl()
    buffer = BytesIO()

    # Basics
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.CAINFO, certifi.where())

    # NOTE: this is important for multithreading
    curl.setopt(pycurl.NOSIGNAL, True)

    if verbose:
        curl.setopt(pycurl.VERBOSE, True)

    # Method
    method = method.upper()

    if method == "POST":
        curl.setopt(pycurl.POST, True)
    elif method == "PUT":
        curl.setopt(pycurl.PUT, True)
    elif method != "GET":
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
    if headers is not None:
        curl_headers = [
            b"%s: %s" % (n.encode("ascii"), v.encode("latin1"))
            for n, v in headers.items()
        ]
        curl.setopt(pycurl.HTTPHEADER, curl_headers)

    # Reading headers
    response_headers = HTTPHeaderDict()

    def header_function(header_line):
        header_line = header_line.decode("iso-8859-1")

        if ":" not in header_line:
            return

        name, value = header_line.split(":", 1)

        name = name.strip()
        value = value.strip()

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

    # Performing
    try:
        curl.perform()
    except pycurl.error as error:
        if error.args[0] == pycurl.E_ABORTED_BY_CALLBACK:
            raise CancelledRequestError

        raise error

    status = curl.getinfo(pycurl.HTTP_CODE)

    curl.close()

    return PycurlResult(
        url=url, body=buffer.getvalue(), headers=response_headers, status=status
    )
