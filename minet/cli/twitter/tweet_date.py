# =============================================================================
# Minet Twitter Tweet-date CLI Action
# =============================================================================
#
# Logic of the `tw tweet-date` action.
#
import re

from minet.cli.utils import with_enricher_and_loading_bar
from twitwi.utils import get_dates_from_id
from ural.twitter import parse_twitter_url, TwitterTweet, TwitterUser, TwitterList

ID_RE = re.compile(r"^[0-9]+$")


@with_enricher_and_loading_bar(
    headers=["timestamp_utc", "locale_time"],
    title="Inferring tweet dates",
    unit="tweets",
)
def action(cli_args, enricher, loading_bar):
    for row, tweet in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            tweet_id = tweet

            tweet_parsed = parse_twitter_url(tweet)
            if isinstance(tweet_parsed, TwitterTweet):
                tweet_id = tweet_parsed.id
            elif isinstance(tweet_parsed, (TwitterUser, TwitterList)) or (
                not tweet_parsed and not ID_RE.match(tweet)
            ):
                loading_bar.print("%s is not a tweet id or url." % tweet)
                continue

            try:
                result = get_dates_from_id(tweet_id, locale=cli_args.timezone)

            except (ValueError, TypeError):
                enricher.writerow(row)
                continue

            enricher.writerow(row, list(result))
