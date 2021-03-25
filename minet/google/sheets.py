# =============================================================================
# Minet Google Sheets Functions
# =============================================================================
#
# Functions related to google sheets.
#
import browser_cookie3
from ural import is_url
from ural.google import (
    parse_google_drive_url,
    GoogleDriveFile,
    GoogleDrivePublicLink
)

from minet.utils import CookieResolver, create_pool, request
from minet.constants import COOKIE_BROWSERS
from minet.google.exceptions import (
    GoogleSheetsInvalidTargetError,
    GoogleSheetsInvalidContentTypeError,
    GoogleSheetsMissingCookieError,
    GoogleSheetsNotFoundError,
    GoogleSheetsUnauthorizedError
)

POOL = create_pool()


def append_authuser(url, authuser):
    url += '&authuser=%i' % authuser
    return url


def export_google_sheets_as_csv(url, cookie=None):
    if is_url(url):
        parsed = parse_google_drive_url(url)

        if parsed is None or parsed.type != 'spreadsheets':
            raise GoogleSheetsInvalidTargetError
    else:
        parsed = GoogleDriveFile('spreadsheets', url)

    export_url = parsed.get_export_url()

    if cookie is not None and cookie in COOKIE_BROWSERS:
        jar = getattr(browser_cookie3, cookie)()
        resolver = CookieResolver(jar)
        cookie = resolver(export_url)

        if cookie is None:
            raise GoogleSheetsMissingCookieError

    err, response = request(POOL, export_url, cookie=cookie)

    if err:
        raise err

    if response.status == 404:
        raise GoogleSheetsNotFoundError

    if response.status == 401:
        raise GoogleSheetsUnauthorizedError

    if 'csv' not in response.headers.get('Content-Type', '').lower():
        raise GoogleSheetsInvalidContentTypeError

    return response.data.decode('utf-8')
