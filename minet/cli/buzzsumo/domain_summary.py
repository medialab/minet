# =============================================================================
# Minet BuzzSumo Domain Summary CLI Action
# =============================================================================
#
# Logic of the `bz domain-summary` action.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.buzzsumo import BuzzSumoAPIClient
from minet.buzzsumo.exceptions import BuzzSumoInvalidTokenError
from minet.buzzsumo.utils import (
    convert_string_date_into_timestamp
)


SUMMARY_HEADERS = [
    'total_results',
    'total_pages'
]


def buzzsumo_domain_summary_action(cli_args):

    begin_timestamp = convert_string_date_into_timestamp(cli_args.begin_date)
    end_timestamp = convert_string_date_into_timestamp(cli_args.end_date)

    client = BuzzSumoAPIClient(cli_args.token)

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

        try:
            data = client.domain_summary(domain_name, begin_timestamp, end_timestamp)
        except BuzzSumoInvalidTokenError:
            loading_bar.die('Your BuzzSumo token is invalid!')

        enricher.writerow(row, [data['total_results'], data['total_pages']])
        loading_bar.update()
