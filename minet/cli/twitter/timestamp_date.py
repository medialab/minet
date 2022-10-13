# =============================================================================
# Minet Twitter Timestamp-date CLI Action
# =============================================================================
#
# Logic of the `tw timestamp-date` action.
#
import casanova

from minet.cli.utils import LoadingBar
from twitwi.utils import get_dates_from_id
from ural.twitter import parse_twitter_url, TwitterTweet


def twitter_timestamp_date_action(cli_args):

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=["timestamp_utc", "locale_date"],
    )

    loading_bar = LoadingBar("Getting tweets timestamp and date", unit="tweet")

    for row, tweet in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        tweet_id = tweet

        tweet_parsed = parse_twitter_url(tweet)
        if isinstance(tweet_parsed, TwitterTweet):
            tweet_id = tweet_parsed[1]

        tz = None

        if cli_args.locale:
            tz = cli_args.locale

        result = get_dates_from_id(tweet_id, tz)
        enricher.writerow(row, [r for r in result])
