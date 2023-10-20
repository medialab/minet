from playwright.async_api import Error as PlaywrightError

from minet.exceptions import (
    BrowserError,
    BrowserNameNotResolvedError,
    BrowserUnknownError,
)


def convert_playwright_error(error: PlaywrightError) -> BrowserError:
    if "net::ERR_NAME_NOT_RESOLVED" in error.message:
        return BrowserNameNotResolvedError()

    return BrowserUnknownError()
