# =============================================================================
# Minet BuzzSumo Domain CLI Action
# =============================================================================
#
# Logic of the `bz domain` action.
#
from minet.buzzsumo import BuzzSumoAPIClient
from minet.buzzsumo.types import BuzzsumoArticle
from minet.cli.buzzsumo.utils import with_buzzsumo_fatal_errors
from minet.cli.utils import with_enricher_and_loading_bar


@with_buzzsumo_fatal_errors
@with_enricher_and_loading_bar(
    title="Retrieving articles",
    unit="articles",
    headers=BuzzsumoArticle,
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
