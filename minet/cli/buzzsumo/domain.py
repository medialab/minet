# =============================================================================
# Minet BuzzSumo Domain CLI Action
# =============================================================================
#
# Logic of the `bz domain` action.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.buzzsumo import BuzzSumoAPIClient
from minet.buzzsumo.constants import ARTICLES_CSV_HEADERS
from minet.buzzsumo.exceptions import (
    BuzzSumoInvalidQueryError,
    BuzzSumoInvalidTokenError,
)


def buzzsumo_domain_action(cli_args):

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
        try:
            for article in client.domain_articles(
                domain_name, cli_args.begin_date, cli_args.end_date
            ):
                loading_bar.update()
                enricher.writerow(row, article.as_csv_row())
        except BuzzSumoInvalidTokenError:
            loading_bar.die("Your BuzzSumo token is invalid!")
        except BuzzSumoInvalidQueryError as e:
            loading_bar.die(
                "Invalid query: %s" % e.url + "\nMessage from the API: %s" % e
            )

        loading_bar.inc("domains")
