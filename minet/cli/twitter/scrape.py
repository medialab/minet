# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
#
import casanova
from twitwi.constants import TWEET_FIELDS, USER_FIELDS
from twitwi import format_tweet_as_csv_row, format_user_as_csv_row

from minet.utils import PseudoFStringFormatter
from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIScraper
from minet.twitter.exceptions import TwitterPublicAPIOverCapacityError
from minet.twitter.constants import ADDITIONAL_TWEET_FIELDS

CUSTOM_FORMATTER = PseudoFStringFormatter()


def format_meta_row(meta):
    if meta is None:
        return [''] * len(ADDITIONAL_TWEET_FIELDS)

    return [
        meta.get('intervention_type'),
        meta.get('intervention_text'),
        meta.get('intervention_url')
    ]


def twitter_scrape_action(cli_args):
    scraper = TwitterAPIScraper()

    if cli_args.items == 'tweets':
        # Stats
        loading_bar = LoadingBar(
            'Collecting tweets',
            total=cli_args.limit,
            unit='tweet',
            stats={'tokens': 1, 'queries': 0}
        )

        enricher = casanova.enricher(
            cli_args.file,
            cli_args.output,
            add=TWEET_FIELDS + ADDITIONAL_TWEET_FIELDS,
            keep=cli_args.select
        )

    if cli_args.items == 'users':
        # Stats
        loading_bar = LoadingBar(
            'Collecting users',
            total=cli_args.limit,
            unit='user',
            stats={'tokens': 1, 'queries': 0}
        )

        enricher = casanova.enricher(
            cli_args.file,
            cli_args.output,
            add=USER_FIELDS,
            keep=cli_args.select
        )

    for row, query in enricher.cells(cli_args.query, with_rows=True):

        # Templating?
        if cli_args.query_template is not None:
            query = CUSTOM_FORMATTER.format(
                cli_args.query_template,
                value=query
            )

        loading_bar.print('Searching for "%s"' % query)
        loading_bar.inc('queries')

        if cli_args.items == 'tweets':
            iterator = scraper.search_tweets(
                query,
                limit=cli_args.limit,
                include_referenced_tweets=cli_args.include_refs,
                with_meta=True
            )

            try:
                for tweet, meta in iterator:
                    loading_bar.update()

                    tweet_row = format_tweet_as_csv_row(tweet)
                    enricher.writerow(row, tweet_row + format_meta_row(meta))
            except TwitterPublicAPIOverCapacityError:
                loading_bar.die('Got an "Over Capacity" error. Shutting down...')

        if cli_args.items == 'users':
            iterator = scraper.search_users(
                query,
                limit=cli_args.limit
            )

            try:
                for user in iterator:
                    loading_bar.update()

                    user_row = format_user_as_csv_row(user)
                    enricher.writerow(row, user_row)
            except TwitterPublicAPIOverCapacityError:
                loading_bar.die('Got an "Over Capacity" error. Shutting down...')
