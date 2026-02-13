# =============================================================================
# Minet Twitter Tweets CLI Action
# =============================================================================
#
# Logic of the `tw tweets` action.
#
from casanova import Enricher
import casanova
import casanova.ndjson as ndjson

from twitwi.constants import TWEET_FIELDS
from twitwi import format_tweet_as_csv_row
from ural.twitter import is_twitter_url, parse_twitter_url, TwitterTweet

from minet.cli.utils import with_enricher_and_loading_bar, with_loading_bar
from minet.cli.loading_bar import LoadingBar
from minet.twitter import TwitterUnauthenticatedAPIScraper


@with_enricher_and_loading_bar(
    headers=TWEET_FIELDS,
    title="Scraping",
    unit="tweets",
)
def action_normalize(cli_args, enricher: Enricher, loading_bar: LoadingBar):
    scraper = TwitterUnauthenticatedAPIScraper()

    for row, tweet_id_or_url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            tweet_id = tweet_id_or_url

            if is_twitter_url(tweet_id_or_url):
                parsed = parse_twitter_url(tweet_id_or_url)

                if isinstance(parsed, TwitterTweet):
                    tweet_id = parsed.id

            tweet = scraper.get_normalized_tweet(tweet_id)
            if tweet:
                tweet = format_tweet_as_csv_row(tweet)
                enricher.writerow(row, tweet)
            else:
                enricher.writerow(row)


@with_loading_bar(
    title="Scraping",
    unit="tweets",
)
def action_raw(cli_args, loading_bar: LoadingBar):
    scraper = TwitterUnauthenticatedAPIScraper()

    reader = casanova.reader(cli_args.input, total=cli_args.total)
    writer = ndjson.writer(cli_args.output)

    for tweet_id_or_url in reader.cells(cli_args.column):
        with loading_bar.step():
            tweet_id = tweet_id_or_url

            if is_twitter_url(tweet_id_or_url):
                parsed = parse_twitter_url(tweet_id_or_url)

                if isinstance(parsed, TwitterTweet):
                    tweet_id = parsed.id

            tweet = scraper.get_tweet(tweet_id)
            tweet = {'tweet_id': tweet_id, 'tweet': tweet}
            writer.writerow(tweet)


def action(cli_args):
    if cli_args.raw:
        action_raw(cli_args)  # type: ignore
    else:
        action_normalize(cli_args)  # type: ignore
