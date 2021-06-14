# =============================================================================
# Minet Twitter CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the twitter actions.
#
import casanova
from twitwi import TwitterWrapper
from twitter import TwitterHTTPError

from minet.web import create_request_retryer
from minet.cli.utils import LoadingBar


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

        # TODO: this is temp debug
        def listener(event, data):
            loading_bar.print(event)
            loading_bar.print(repr(data))

        wrapper = TwitterWrapper(
            cli_args.access_token,
            cli_args.access_token_secret,
            cli_args.api_key,
            cli_args.api_secret_key,
            listener=listener
        )

        # TODO: I should probably create a twitter api client high-level abstraction
        # to be used with all the relevant cli commands
        retryer = create_request_retryer()

        resuming_state = None

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
                wrapper_kwargs = {'user_id': user}
            else:
                wrapper_kwargs = {'screen_name': user}

            while next_cursor != 0:
                wrapper_kwargs['cursor'] = next_cursor

                skip_in_output = None

                if resuming_state:
                    skip_in_output = resuming_state.values_to_skip
                    resuming_state = None

                try:
                    result = retryer(wrapper.call, [method_name, 'ids'], **wrapper_kwargs)
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
