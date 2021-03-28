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
    GoogleDriveFile
)

from minet.web import CookieResolver, request
from minet.constants import COOKIE_BROWSERS
from minet.google.exceptions import (
    GoogleSheetsInvalidTargetError,
    GoogleSheetsInvalidContentTypeError,
    GoogleSheetsMissingCookieError,
    GoogleSheetsNotFoundError,
    GoogleSheetsUnauthorizedError,
    GoogleSheetsMaxAttemptsExceeded
)


def append_authuser(url, authuser):
    url += '&authuser=%i' % authuser
    return url


def export_google_sheets_as_csv(url, cookie=None, authuser=None, max_authuser_attempts=4):
    if is_url(url):
        parsed = parse_google_drive_url(url)

        if parsed is None or parsed.type != 'spreadsheets':
            raise GoogleSheetsInvalidTargetError
    else:
        parsed = GoogleDriveFile('spreadsheets', url)

    base_export_url = parsed.get_export_url()
    export_url = base_export_url

    if authuser is not None:
        if not isinstance(authuser, int) or authuser < 0:
            raise TypeError('authuser should be an int >= 0')

        export_url = append_authuser(export_url, authuser)
        max_authuser_attempts = 1
    else:
        authuser = 0

    if cookie is not None and cookie in COOKIE_BROWSERS:
        jar = getattr(browser_cookie3, cookie)()
        resolver = CookieResolver(jar)
        cookie = resolver(export_url)

        if cookie is None:
            raise GoogleSheetsMissingCookieError

    attempts = max_authuser_attempts

    while True:
        attempts -= 1

        err, response = request(export_url, cookie=cookie)

        if err:
            raise err

        if response.status == 404:
            raise GoogleSheetsNotFoundError

        if response.status == 401:
            raise GoogleSheetsUnauthorizedError

        if response.status == 403:
            authuser += 1

            if attempts != 0:
                export_url = append_authuser(base_export_url, authuser)
                continue

            raise GoogleSheetsMaxAttemptsExceeded

        if 'csv' not in response.headers.get('Content-Type', '').lower():
            raise GoogleSheetsInvalidContentTypeError

        break

    return response.data.decode('utf-8')
