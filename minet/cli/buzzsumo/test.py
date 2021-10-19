# =============================================================================
# Minet BuzzSumo Test CLI Action
# =============================================================================
#
# Logic of the `bz test` action.
#

from datetime import datetime, timedelta
import csv

import requests


BUZZSUMO_TEST_CSV_HEADERS = [
    'X-RateLimit-Month-Remaining',
    'X-RateLimit-Limit',
    'X-RateLimit-Remaining',
    'X-RateLimit-Reset'
]


def buzzsumo_test_action(cli_args):

    writer = csv.writer(cli_args.output)
    writer.writerow(BUZZSUMO_TEST_CSV_HEADERS)

    params = {
        'api_key': cli_args.token,
        'q': 'lemonde.fr',
        'begin_date': datetime.now().timestamp(),
        'end_date': datetime.now().timestamp() - 60 * 60,
        'num_results': 100,
    }

    r = requests.get('https://api.buzzsumo.com/search/articles.json', params=params)

    if r.status_code == 200:
        writer.writerow([r.headers[column] for column in BUZZSUMO_TEST_CSV_HEADERS])
    else:
        writer.writerow(['bad request', r.status_code, '', ''])

    # writer.writerow(r.headers.keys())
    # writer.writerow(r.headers.values())
