# =============================================================================
# Minet Google Sheets Functions
# =============================================================================
#
# Functions related to google sheets.
#
import browser_cookie3
from ural import is_url
from ural.google import extract_id_from_google_drive_url

from minet.utils import CookieResolver, create_pool, request
from minet.constants import COOKIE_BROWSERS
from minet.google.exceptions import (
    GoogleSheetsInvalidTargetError,
    GoogleSheetsInvalidContentTypeError,
    GoogleSheetsMissingCookieError
)

POOL = create_pool()


def forge_export_url(drive_id, authuser=None):
    url = 'https://docs.google.com/spreadsheets/d/%s/export?exportFormat=csv' % drive_id

    if authuser is not None:
        url += '&authuser=%i' % authuser

    return url


def export_google_sheets_as_csv(url, cookie=None):
    if is_url(url):
        drive_id = extract_id_from_google_drive_url(url)
    else:
        drive_id = url

    if drive_id is None:
        raise GoogleSheetsInvalidTargetError

    authuser = 0
    export_url = forge_export_url(drive_id, authuser)

    if cookie is not None and cookie in COOKIE_BROWSERS:
        jar = getattr(browser_cookie3, cookie)
        resolver = CookieResolver(jar)
        cookie = resolver(export_url)

        if cookie is None:
            raise GoogleSheetsMissingCookieError

    err, response = request(POOL, export_url, cookie=cookie)

    if err:
        raise err

    if 'csv' not in response.headers.get('Content-Type', '').lower():
        raise GoogleSheetsInvalidContentTypeError

    return response.data.decode('utf-8')
