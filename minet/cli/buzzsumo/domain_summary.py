# =============================================================================
# Minet BuzzSumo Domain Summary CLI Action
# =============================================================================
#
# Logic of the `bz domain-summary` action.
#
from datetime import datetime

import casanova

from minet.web import request_json


URL_TEMPLATE = 'https://api.buzzsumo.com/search/articles.json?api_key=%s'

SUMMARY_HEADERS = [
    'total_results',
    'total_pages'
]


def convert_string_date_to_timestamp(date):
    return datetime.strptime(date, '%Y-%m-%d').timestamp()


def buzzsumo_domain_summary_action(cli_args):

    base_url = URL_TEMPLATE % cli_args.token

    begin_date = convert_string_date_to_timestamp(cli_args.begin_date)
    base_url += '&begin_date=%s' % begin_date

    end_date = convert_string_date_to_timestamp(cli_args.end_date)
    base_url += '&end_date=%s' % end_date

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=SUMMARY_HEADERS,
    )

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):
        url = base_url + '&q=%s' % domain_name
        print('test', url)
