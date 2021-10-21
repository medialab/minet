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

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient


def twitter_user_search_action(cli_args):

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
        unit='user'
    )

    for row, query in enricher.cells(cli_args.query, with_rows=True):

        kwargs = {'q': query, 'count': 20, 'include_entities': True}

        loading_bar.print('Searching for "%s" users' % query)
        loading_bar.inc('queries')

        indexed_users = set()

        for page in range(1, 52):
            kwargs['page'] = page

            result = None

            try:
                result = client.call(['users', 'search'], **kwargs)

            except TwitterHTTPError as e:
                raise

            if not result:
                break

            user_count = 0

            for user in result:
                user = normalize_user(user)

                if user['id'] in indexed_users:
                    user_count += 1
                    continue

                if user_count == 20:
                    break

                indexed_users.add(user['id'])

                user_row = format_user_as_csv_row(user)

                enricher.writerow(row, user_row)

                loading_bar.update()

            if user_count == 20:
                break

            if len(result) < 20:
                break
