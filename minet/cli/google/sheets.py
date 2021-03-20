# =============================================================================
# Minet Google Sheets CLI Action
# =============================================================================
#
# Logic of the `google sheets` action.
#
from ural import is_url
from ural.google import extract_id_from_google_drive_url

from minet.utils import grab_cookies
from minet.cli.utils import die


def google_sheets_action(namespace):
    if is_url:
        drive_id = extract_id_from_google_drive_url(namespace.url)
    else:
        drive_id = namespace.url

    if not drive_id:
        die('Could not extract a valid google drive id from provided argument!')

    get_cookie = grab_cookies(namespace.cookie)

    if get_cookie is None:
        die('Could not grab cookies from %s' % namespace.cookie)

    export_url = 'https://docs.google.com/spreadsheets/d/%s/export?exportFormat=csv' % drive_id

    cookie = get_cookie(export_url)

    print(cookie)
