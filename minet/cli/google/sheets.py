# =============================================================================
# Minet Google Sheets CLI Action
# =============================================================================
#
# Logic of the `google sheets` action.
#
from browser_cookie3 import BrowserCookieError

from minet.cli.exceptions import FatalError
from minet.google import export_google_sheets_as_csv
from minet.google.exceptions import (
    GoogleSheetsInvalidTargetError,
    GoogleSheetsInvalidContentTypeError,
    GoogleSheetsMissingCookieError,
    GoogleSheetsNotFoundError,
    GoogleSheetsUnauthorizedError,
    GoogleSheetsMaxAttemptsExceeded,
)


def action(cli_args):
    try:
        data = export_google_sheets_as_csv(
            cli_args.url, cookie=cli_args.cookie, authuser=cli_args.authuser
        )
    except GoogleSheetsInvalidTargetError:
        raise FatalError(
            "Could not extract a valid google sheets id from provided argument!"
        )
    except BrowserCookieError:
        raise FatalError("Could not extract cookie from %s!" % cli_args.cookie)
    except GoogleSheetsMissingCookieError:
        raise FatalError("Did not find a relevant cookie!")
    except GoogleSheetsInvalidContentTypeError:
        raise FatalError("Could not export spreadsheet as CSV!")
    except GoogleSheetsNotFoundError:
        raise FatalError("Could not find spreadsheet (404)!")
    except GoogleSheetsUnauthorizedError:
        raise FatalError(
            "You don't have access to this spreadsheet. Did you forget to set --cookie?"
        )
    except GoogleSheetsMaxAttemptsExceeded:
        raise FatalError(
            "Maximum number of attempts exceeded! You can still set --authuser if you logged in numerous google accounts at once."
        )

    cli_args.output.write(data)
