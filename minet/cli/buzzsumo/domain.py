# =============================================================================
# Minet BuzzSumo Domain CLI Action
# =============================================================================
#
# Logic of the `bz domain` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.buzzsumo.utils import with_buzzsumo_fatal_errors
from minet.buzzsumo import BuzzSumoAPIClient
from minet.buzzsumo.constants import ARTICLES_CSV_HEADERS


@with_buzzsumo_fatal_errors
@with_enricher_and_loading_bar(
    title="Retrieving articles",
    unit="articles",
    headers=ARTICLES_CSV_HEADERS,
    nested=True,
)
def action(cli_args, enricher, loading_bar):
    client = BuzzSumoAPIClient(cli_args.token)

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(domain_name):

            for article in client.domain_articles(
                domain_name, cli_args.begin_date, cli_args.end_date
            ):
                loading_bar.nested_advance()
                enricher.writerow(row, article.as_csv_row())
