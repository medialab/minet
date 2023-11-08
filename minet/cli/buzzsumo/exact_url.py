# =============================================================================
# Minet BuzzSumo Exact URL CLI Action
# =============================================================================
#
# Logic of the `bz exact-url` action.
#
from minet.buzzsumo import BuzzSumoAPIClient
from minet.buzzsumo.types import BuzzsumoArticle
from minet.cli.buzzsumo.utils import with_buzzsumo_fatal_errors
from minet.cli.utils import with_enricher_and_loading_bar


@with_buzzsumo_fatal_errors
@with_enricher_and_loading_bar(
    title="Retrieving url metadata", headers=BuzzsumoArticle, unit="urls"
)
def action(cli_args, enricher, loading_bar):
    client = BuzzSumoAPIClient(cli_args.token)

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            data = client.exact_url(url, cli_args.begin_date, cli_args.end_date)
            if data:
                enricher.writerow(row, data.as_csv_row())
            else:
                enricher.writerow(row)
