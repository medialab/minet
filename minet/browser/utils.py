from typing import Union

from tempfile import gettempdir
from os.path import expanduser, join
from playwright.async_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

from minet.exceptions import (
    BrowserError,
    BrowserNameNotResolvedError,
    BrowserConnectionAbortedError,
    BrowserConnectionRefusedError,
    BrowserConnectionClosedError,
    BrowserTimeoutError,
    BrowserUnknownError,
    BrowserSSLError,
    BrowserHTTPResponseCodeFailureError,
    BrowserConnectionTimeoutError,
    BrowserContextAlreadyClosedError,
    BrowserSocketError,
)
from minet.browser.constants import BROWSERS_PATH

AnyPlaywrightError = Union[PlaywrightError, PlaywrightTimeoutError]


def convert_playwright_error(error: AnyPlaywrightError) -> BrowserError:
    lower_message = error.message.lower()

    if isinstance(error, PlaywrightTimeoutError):
        return BrowserTimeoutError()

    if "net::ERR_NAME_NOT_RESOLVED" in error.message:
        return BrowserNameNotResolvedError()

    if "net::ERR_ABORTED" in error.message:
        return BrowserConnectionAbortedError()

    if "net::ERR_CONNECTION_REFUSED" in error.message:
        return BrowserConnectionRefusedError()

    if "net::ERR_CONNECTION_CLOSED" in error.message:
        return BrowserConnectionClosedError()

    if (
        "net::ERR_CERT_AUTHORITY_INVALID" in error.message
        or "net::ERR_CERT_COMMON_NAME_INVALID" in error.message
    ):
        return BrowserSSLError()

    if "net::ERR_HTTP_RESPONSE_CODE_FAILURE" in error.message:
        return BrowserHTTPResponseCodeFailureError()

    if "net::ERR_CONNECTION_TIMED_OUT" in error.message:
        return BrowserConnectionTimeoutError()

    if (
        "target page, context or browser has been closed" in lower_message
        or "browser closed" in lower_message
        or "maybe frame was detached?" in lower_message
    ):
        return BrowserContextAlreadyClosedError()

    if "net::ERR_SOCKET_NOT_CONNECTED" in error.message:
        return BrowserSocketError()

    return BrowserUnknownError()


def get_browsers_path() -> str:
    return expanduser(join("~", BROWSERS_PATH))


def get_temp_persistent_context_path() -> str:
    return join(gettempdir(), "minet-browser-temporary-persistent-context")
