# =============================================================================
# Minet BuzzSumo Domain Summary CLI Action
# =============================================================================
#
# Logic of the `bz domain-summary` action.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.buzzsumo.utils import (
    convert_string_date_into_timestamp,
    construct_url,
    URL_TEMPLATE,
    call_buzzsumo_once
)


SUMMARY_HEADERS = [
    'total_results',
    'total_pages'
]


def buzzsumo_domain_summary_action(cli_args):

    begin_date = convert_string_date_into_timestamp(cli_args.begin_date)
    end_date = convert_string_date_into_timestamp(cli_args.end_date)

    base_url = construct_url(URL_TEMPLATE, cli_args.token, begin_date, end_date)

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

        url = base_url + '&q=%s' % domain_name
        data, _ = call_buzzsumo_once(url)

        enricher.writerow(row, [int(data['total_results']), data['total_pages']])
        loading_bar.update()
