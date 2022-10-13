# =============================================================================
# Minet Twitter Tweet-date CLI Action
# =============================================================================
#
# Logic of the `tw tweet-date` action.
#
import casanova

from minet.cli.utils import LoadingBar
from twitwi.utils import get_dates_from_id
from ural.twitter import parse_twitter_url, TwitterTweet


def twitter_tweet_date_action(cli_args):

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=["timestamp_utc", "locale_time"],
    )

    loading_bar = LoadingBar("Getting tweets timestamp and date", unit="tweet")

    for row, tweet in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        tweet_id = tweet

        tweet_parsed = parse_twitter_url(tweet)
        if isinstance(tweet_parsed, TwitterTweet):
            tweet_id = tweet_parsed.id

        try:
            result = get_dates_from_id(tweet_id, locale=cli_args.timezone)

        except (ValueError, TypeError):
            loading_bar.inc("errors")
            enricher.writerow(row)

            continue

        enricher.writerow(row, list(result))
