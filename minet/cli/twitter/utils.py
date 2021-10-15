# =============================================================================
# Minet Twitter CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the twitter actions.
#
import casanova
import re
from twitter import TwitterHTTPError

from minet.cli.utils import LoadingBar, die
from minet.twitter import TwitterAPIClient


def make_twitter_action(method_name, csv_headers):

    def action(cli_args):
        enricher = casanova.batch_enricher(
            cli_args.file,
            cli_args.output,
            keep=cli_args.select,
            add=csv_headers
        )

        loading_bar = LoadingBar(
            desc='Retrieving ids',
            unit=method_name[:-1],
            stats={
                'users': 0
            }
        )

        client = TwitterAPIClient(
            cli_args.access_token,
            cli_args.access_token_secret,
            cli_args.api_key,
            cli_args.api_secret_key
        )

        resuming_state = None

        if cli_args.ids:
            if not is_id(cli_args.column, enricher):
                die('\nThe column given as argument doesn\'t contain user ids, you have probably given user screen names as argument instead.')
        else:
            if not is_screen_name(cli_args.column, enricher):
                die('\nThe column given as argument probably doesn\'t contain user screen names, you have probably given user ids as argument instead.')
                # force flag to add

        if cli_args.resume:
            resuming_state = cli_args.output.pop_state()

        for row, user in enricher.cells(cli_args.column, with_rows=True):
            loading_bar.update_stats(user=user)

            all_ids = []
            next_cursor = -1
            result = None

            if resuming_state is not None and resuming_state.last_cursor:
                next_cursor = int(resuming_state.last_cursor)

            if cli_args.ids:
                client_kwargs = {'user_id': user}
            else:
                client_kwargs = {'screen_name': user}

            while next_cursor != 0:
                client_kwargs['cursor'] = next_cursor

                skip_in_output = None

                if resuming_state:
                    skip_in_output = resuming_state.values_to_skip
                    resuming_state = None

                try:
                    result = client.call([method_name, 'ids'], **client_kwargs)
                except TwitterHTTPError as e:

                    # The user does not exist
                    loading_bar.inc('users_not_found')
                    break

                if result is not None:
                    all_ids = result.get('ids', [])
                    next_cursor = result.get('next_cursor', 0)

                    loading_bar.update(len(all_ids))

                    batch = []

                    for user_id in all_ids:
                        if skip_in_output and user_id in skip_in_output:
                            continue

                        batch.append([user_id])

                    enricher.writebatch(row, batch, next_cursor or None)
                else:
                    next_cursor = 0

            loading_bar.inc('users')

    return action


def is_id(column, enricher):

    characters = re.compile(r'[A-Za-z_]')

    for item in enricher.cells(column, with_rows=True):
        matches = re.findall(characters, item[1])
        if matches:
            return False
        else:
            return True


def is_screen_name(column, enricher):

    numbers = re.compile(r'[0-9]+')

    for item in enricher.cells(column, with_rows=True):
        matches = numbers.fullmatch(item[1])
        if matches:
            return False
        else:
            return True
