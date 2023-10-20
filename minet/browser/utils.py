from typing import Union

from playwright.async_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

from minet.exceptions import (
    BrowserError,
    BrowserNameNotResolvedError,
    BrowserConnectionAbortedError,
    BrowserConnectionRefusedError,
    BrowserTimeoutError,
    BrowserUnknownError,
    BrowserSSLError,
)

AnyPlaywrightError = Union[PlaywrightError, PlaywrightTimeoutError]


def convert_playwright_error(error: AnyPlaywrightError) -> BrowserError:
    if isinstance(error, PlaywrightTimeoutError):
        return BrowserTimeoutError()

    if "net::ERR_NAME_NOT_RESOLVED" in error.message:
        return BrowserNameNotResolvedError()

    if "net::ERR_ABORTED" in error.message:
        return BrowserConnectionAbortedError()

    if "net::ERR_CONNECTION_REFUSED" in error.message:
        return BrowserConnectionRefusedError()

    if (
        "net::ERR_CERT_AUTHORITY_INVALID" in error.message
        or "net::ERR_CERT_COMMON_NAME_INVALID" in error.message
    ):
        return BrowserSSLError()

    return BrowserUnknownError()
