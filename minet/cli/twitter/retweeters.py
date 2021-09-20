# =============================================================================
# Minet Twitter Retweeters CLI Action
# =============================================================================
#
# Logic of the `tw retweeters` action.
#
import casanova

from twitter import TwitterHTTPError

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient


REPORT_HEADERS = [
    'retweeter_id'
]


def twitter_retweeters_action(cli_args):

    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key
    )

    enricher = casanova.batch_enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=REPORT_HEADERS,
        total=cli_args.total
    )

    loading_bar = LoadingBar(
        'Retrieving tweets retweeters',
        total=enricher.total,
        unit=' retweeter_id',
        stats={
            'retweeters': 0
        }
    )

    resuming_state = None

    if cli_args.resume:
        resuming_state = cli_args.output.pop_state()

    for row, tweet in enricher.cells(cli_args.column, with_rows=True):
        kwargs = {'_id': tweet}
        kwargs['tweet_mode'] = 'extended'
        # kwargs['count'] = 100
        loading_bar.update_stats(tweet=tweet)

        all_ids = []
        next_cursor = -1
        result = None

        if resuming_state is not None and resuming_state.last_cursor:
            next_cursor = int(resuming_state.last_cursor)

        while next_cursor != 0:
            kwargs['cursor'] = next_cursor

            skip_in_output = None

            if resuming_state:
                skip_in_output = resuming_state.values_to_skip
                resuming_state = None

            try:
                result = client.call(['statuses', 'retweeters', 'ids'], **kwargs)
            except TwitterHTTPError as e:

                # The tweet does not exist
                loading_bar.inc('tweet_not_found')
                break

            if result is not None:
                all_ids = result.get('ids', [])
                next_cursor = result.get('next_cursor', 0)

                loading_bar.update(len(all_ids))

                batch = []

                for retweeter_id in all_ids:
                    if skip_in_output and retweeter_id in skip_in_output:
                        continue

                    batch.append([retweeter_id])

                enricher.writebatch(row, batch, next_cursor or None)
            else:
                next_cursor = 0

        loading_bar.inc('tweets')
