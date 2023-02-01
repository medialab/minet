# =============================================================================
# Minet BuzzSumo Domain CLI Action
# =============================================================================
#
# Logic of the `bz domain` action.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.cli.buzzsumo.utils import with_buzzsumo_fatal_errors
from minet.buzzsumo import BuzzSumoAPIClient
from minet.buzzsumo.constants import ARTICLES_CSV_HEADERS


@with_buzzsumo_fatal_errors
def action(cli_args):

    client = BuzzSumoAPIClient(cli_args.token)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=ARTICLES_CSV_HEADERS,
    )

    loading_bar = LoadingBar(desc="Retrieving articles", unit="article")

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.print('Retrieving articles for "%s"' % domain_name)

        for article in client.domain_articles(
            domain_name, cli_args.begin_date, cli_args.end_date
        ):
            loading_bar.update()
            enricher.writerow(row, article.as_csv_row())

        loading_bar.inc("domains")
