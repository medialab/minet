# =============================================================================
# Minet Twitter Users CLI Action
# =============================================================================
#
# Logic of the `tw users` action.
#
import casanova
from twitwi import (
    TwitterWrapper,
    normalize_user,
    format_user_as_csv_row
)
from twitter import TwitterHTTPError
from twitwi.constants import USER_FIELDS
from ebbe import as_chunks

from minet.cli.utils import LoadingBar


def twitter_users_action(cli_args):

    wrapper = TwitterWrapper(
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

    for chunk in as_chunks(100, enricher.cells(cli_args.column, with_rows=True)):
        users = ','.join(row[1].lstrip('@') for row in chunk)

        if cli_args.ids:
            wrapper_args = {'user_id': users}
            key = 'id'
        else:
            wrapper_args = {'screen_name': users}
            key = 'screen_name'

        try:
            result = wrapper.call(['users', 'lookup'], **wrapper_args)
        except TwitterHTTPError as e:
            if e.e.code == 404:
                for row, user in chunk:
                    enricher.writerow(row)
            else:
                raise e

            continue

        indexed_result = {}

        for user in result:
            user = normalize_user(user)
            user_row = format_user_as_csv_row(user)
            indexed_result[user[key]] = user_row

        for row, user in chunk:
            user_row = indexed_result.get(user.lstrip('@'))

            enricher.writerow(row, user_row)

        loading_bar.update(len(chunk))
