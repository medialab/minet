# =============================================================================
# Minet Twitter Users Search CLI Action
# =============================================================================
#
# Logic of the `tw users-search` action.
#
import casanova
from twitwi import (
    normalize_user,
    format_user_as_csv_row
)
from twitter import TwitterHTTPError
from twitwi.constants import USER_FIELDS
from ebbe import getpath

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient


def twitter_users_search_action(cli_args):

    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key
    )

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=USER_FIELDS
    )

    loading_bar = LoadingBar(
        desc='Retrieving users',
        total=cli_args.total,
        unit='query'
    )

    for row, query in enricher.cells(cli_args.query, with_rows=True):

        kwargs = {'q': query, 'count': 20}

        loading_bar.print('Searching for "%s" users' % query)
        loading_bar.inc('queries')

        next_page = 0

        while True:
            kwargs['page'] = next_page

            result = None

            try:
                result = client.call(['users', 'search'], **kwargs)

            except TwitterHTTPError as e:
                error_code = getpath(e.response_data, ['errors', 0, 'code'], '')
                if e.e.code == 400 and error_code == 44:
                    break

                else:
                    raise

            next_page += 1

            if result is None:
                break

            for user in result:
                user = normalize_user(user)
                user_row = format_user_as_csv_row(user)

                enricher.writerow(row, user_row)
