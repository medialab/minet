# =============================================================================
# Minet BuzzSumo Domain Summary CLI Action
# =============================================================================
#
# Logic of the `bz domain-summary` action.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.cli.buzzsumo.utils import with_buzzsumo_fatal_errors
from minet.buzzsumo import BuzzSumoAPIClient

SUMMARY_HEADERS = ["total_results", "total_pages"]


@with_buzzsumo_fatal_errors
def action(cli_args):
    client = BuzzSumoAPIClient(cli_args.token)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=SUMMARY_HEADERS,
    )

    loading_bar = LoadingBar(
        desc="Retrieving domain summary", unit="domain", total=enricher.total
    )

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):
        data = client.domain_summary(
            domain_name, cli_args.begin_date, cli_args.end_date
        )

        enricher.writerow(row, [data["total_results"], data["total_pages"]])

        loading_bar.update()
