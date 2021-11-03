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
from minet.buzzsumo.exceptions import BuzzSumoInvalidTokenError
from minet.buzzsumo.utils import convert_string_date_into_timestamp


def buzzsumo_domain_action(cli_args):

    client = BuzzSumoAPIClient(cli_args.token)

    begin_timestamp = convert_string_date_into_timestamp(cli_args.begin_date)
    end_timestamp = convert_string_date_into_timestamp(cli_args.end_date)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=ARTICLES_CSV_HEADERS,
    )

    loading_bar = LoadingBar(
        desc='Retrieving articles',
        unit='article'
    )

    for row, domain_name in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.print('Retrieving articles for "%s"' % domain_name)
        try:
            for article in client.domain_articles(domain_name, begin_timestamp, end_timestamp):
                loading_bar.update()
                enricher.writerow(row, article.as_csv_row())
        except BuzzSumoInvalidTokenError:
            loading_bar.die('Your BuzzSumo token is invalid!')

        loading_bar.inc('domains')
