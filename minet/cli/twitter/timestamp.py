# =============================================================================
# Minet Twitter Tweets CLI Action
# =============================================================================
#
# Logic of the `tw tweets` action.
#
import casanova

from minet.cli.utils import LoadingBar
from twitwi.utils import get_timestamp_from_id
from ural.twitter import parse_twitter_url


def twitter_timestamp_action(cli_args):

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=["timestamp_utc"],
    )

    loading_bar = LoadingBar("Getting tweets timestamp", unit="tweet")

    for row, tweet in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        tweet_id = parse_twitter_url(tweet)[1]
        if not tweet_id:
            tweet_id = tweet

        timestamp = get_timestamp_from_id(tweet_id)
        enricher.writerow(row, [timestamp])
