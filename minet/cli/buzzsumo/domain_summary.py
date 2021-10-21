# =============================================================================
# Minet BuzzSumo Domain Summary CLI Action
# =============================================================================
#
# Logic of the `bz domain-summary` action.
#
from datetime import datetime
import time

import casanova
import requests

from minet.cli.utils import LoadingBar
# from minet.web import request_json


URL_TEMPLATE = 'https://api.buzzsumo.com/search/articles.json?api_key=%s'

SUMMARY_HEADERS = [
    'total_results',
    'total_pages'
]


def convert_string_date_to_timestamp(date):
    return datetime.strptime(date, '%Y-%m-%d').timestamp()


def call_buzzsumo_once(url):

    api_call_attempt = 0

    while True:

        if api_call_attempt == 0:
            start_call_time = time.time()
        # If second try or more, wait an exponential amount of time (first 2 sec, then 4, then 16...)
        else:
            time.sleep(2**(api_call_attempt - 1))

        r = requests.get(url)

        # If first try, add a sleep function so that we wait at least 1.2 seconds between two calls
        if api_call_attempt == 0:
            end_call_time = time.time()
            if (end_call_time - start_call_time) < 1.2:
                time.sleep(1.2 - (end_call_time - start_call_time))

        if r.status_code == 200:
            break
        else:
            print(r.status_code, r.json())
            api_call_attempt += 1

    return r.json()


def buzzsumo_domain_summary_action(cli_args):

    base_url = URL_TEMPLATE % cli_args.token
    base_url += '&num_results=100'

    begin_date = convert_string_date_to_timestamp(cli_args.begin_date)
    base_url += '&begin_date=%s' % begin_date

    end_date = convert_string_date_to_timestamp(cli_args.end_date)
    base_url += '&end_date=%s' % end_date

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=SUMMARY_HEADERS,
    )

    loading_bar = LoadingBar(
        desc='Retrieving domain summary',
        unit='domain',
        total=enricher.total
    )

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):

        loading_bar.update()

        url = base_url + '&q=%s' % domain_name
        response = call_buzzsumo_once(url)

        enricher.writerow(row, [int(response['total_results']), response['total_pages']])
