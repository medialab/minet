# =============================================================================
# Minet Google Sheets CLI Action
# =============================================================================
#
# Logic of the `google sheets` action.
#
from browser_cookie3 import BrowserCookieError

from minet.cli.utils import open_output_file, die
from minet.google import export_google_sheets_as_csv
from minet.google.exceptions import (
    GoogleSheetsInvalidTargetError,
    GoogleSheetsInvalidContentTypeError,
    GoogleSheetsMissingCookieError,
    GoogleSheetsNotFoundError,
    GoogleSheetsUnauthorizedError,
    GoogleSheetsMaxAttemptsExceeded
)


def google_sheets_action(namespace):
    output_file = open_output_file(namespace.output, flag='w')

    try:
        data = export_google_sheets_as_csv(
            namespace.url,
            cookie=namespace.cookie,
            authuser=namespace.authuser
        )
    except GoogleSheetsInvalidTargetError:
        die('Could not extract a valid google sheets id from provided argument!')
    except BrowserCookieError:
        die('Could not extract cookie from %s!' % namespace.cookie)
    except GoogleSheetsMissingCookieError:
        die('Did not find a relevant cookie!')
    except GoogleSheetsInvalidContentTypeError:
        die('Could not export spreadsheet as CSV!')
    except GoogleSheetsNotFoundError:
        die('Could not find spreadsheet (404)!')
    except GoogleSheetsUnauthorizedError:
        die('You don\'t have access to this spreadsheet. Did you forget to set --cookie?')
    except GoogleSheetsMaxAttemptsExceeded:
        die('Maximum number of attempts exceeded! You can still set --authuser if you logged in numerous google accounts at once.')

    output_file.write(data)
    output_file.close()
