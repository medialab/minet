# =============================================================================
# Minet BuzzSumo Domain Summary CLI Action
# =============================================================================
#
# Logic of the `bz domain-summary` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.buzzsumo.utils import with_buzzsumo_fatal_errors
from minet.buzzsumo import BuzzSumoAPIClient

SUMMARY_HEADERS = ["total_results", "total_pages"]


@with_buzzsumo_fatal_errors
@with_enricher_and_loading_bar(
    title="Retrieving domain summary", headers=SUMMARY_HEADERS, unit="domains"
)
def action(cli_args, enricher, loading_bar):
    client = BuzzSumoAPIClient(cli_args.token)

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            data = client.domain_summary(
                domain_name, cli_args.begin_date, cli_args.end_date
            )

            enricher.writerow(row, [data["total_results"], data["total_pages"]])
