# =============================================================================
# Minet Google Sheets CLI Action
# =============================================================================
#
# Logic of the `google sheets` action.
#
from ural import is_url
from ural.google import extract_id_from_google_drive_url

from minet.utils import grab_cookies, create_pool, request
from minet.cli.utils import die, open_output_file


def google_sheets_action(namespace):
    output_file = open_output_file(namespace.output)

    if is_url(namespace.url):
        drive_id = extract_id_from_google_drive_url(namespace.url)
    else:
        drive_id = namespace.url

    if not drive_id:
        die('Could not extract a valid google drive id from provided argument!')

    get_cookie = grab_cookies(namespace.cookie)

    if get_cookie is None:
        die('Could not grab cookies from %s!' % namespace.cookie)

    export_url = 'https://docs.google.com/spreadsheets/d/%s/export?exportFormat=csv' % drive_id

    cookie = get_cookie(export_url)

    if not cookie:
        die('Could not extract relevant cookie from %s!' % namespace.cookie)

    http = create_pool()
    err, response = request(http, export_url, cookie=cookie)

    if err:
        raise err

    if 'csv' not in response.headers['Content-Type']:
        die('Could not export spreadsheet as CSV!')

    output_file.write(response.data.decode('utf-8'))
    output_file.close()
