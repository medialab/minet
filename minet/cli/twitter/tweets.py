# =============================================================================
# Minet Twitter Tweets CLI Action
# =============================================================================
#
# Logic of the `tw tweets` action.
#
from casanova import Enricher
from twitwi.constants import TWEET_FIELDS
from twitwi import format_tweet_as_csv_row
from ural.twitter import is_twitter_url, parse_twitter_url, TwitterTweet

from minet.cli.exceptions import FatalError
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar
from minet.twitter import TwitterAPIScraper
from minet.twitter.exceptions import (
    TwitterPublicAPINotFound,
    TwitterPublicAPIInvalidCookieError,
    TwitterPublicAPIBadAuthError,
)


@with_enricher_and_loading_bar(
    headers=TWEET_FIELDS,
    title="Scraping",
    unit="tweets",
)
def action(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    try:
        scraper = TwitterAPIScraper(cli_args.cookie)
    except TwitterPublicAPIInvalidCookieError:
        raise FatalError(
            [
                "Invalid Twitter cookie!",
                "Try giving another browser to --cookie and sure you are correctly logged in.",
            ]
        )

    for row, tweet_id_or_url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            tweet_id = tweet_id_or_url

            if is_twitter_url(tweet_id_or_url):
                parsed = parse_twitter_url(tweet_id_or_url)

                if isinstance(parsed, TwitterTweet):
                    tweet_id = parsed.id

            try:
                tweet = scraper.request_tweet_details(tweet_id)
                tweet = format_tweet_as_csv_row(tweet)
                enricher.writerow(row, tweet)
            except TwitterPublicAPIBadAuthError as error:
                raise FatalError(
                    "Bad authentication (%i). Double check your --cookie and make sure you are logged in."
                    % error.status
                )
            except TwitterPublicAPINotFound:
                loading_bar.inc_stat("not-found", style="warning")
                enricher.writerow(row)
                continue
