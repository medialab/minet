# =============================================================================
# Minet Twitter Tweet-date CLI Action
# =============================================================================
#
# Logic of the `tw tweet-date` action.
#
import re
import casanova

from minet.cli.utils import LoadingBar
from twitwi.utils import get_dates_from_id
from ural.twitter import parse_twitter_url, TwitterTweet, TwitterUser, TwitterList

ID_RE = re.compile(r"^[0-9]+$")


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
        elif isinstance(tweet_parsed, (TwitterUser, TwitterList)) or (
            not tweet_parsed and not ID_RE.match(tweet)
        ):
            loading_bar.inc("errors")
            loading_bar.print("%s is not a tweet id or url." % tweet)
            continue

        try:
            result = get_dates_from_id(tweet_id, locale=cli_args.timezone)

        except (ValueError, TypeError):
            loading_bar.inc("errors")
            enricher.writerow(row)

            continue

        enricher.writerow(row, list(result))
