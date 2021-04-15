# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
#
import casanova
from twitwi.constants import TWEET_FIELDS
from twitwi import format_tweet_as_csv_row

from minet.utils import prettyprint_seconds, PseudoFStringFormatter
from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIScraper
from minet.twitter.exceptions import (
    TwitterPublicAPIRateLimitError,
    TwitterPublicAPIOverCapacityError
)
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

    def before_sleep(retry_state):
        exc = retry_state.outcome.exception()

        if isinstance(exc, TwitterPublicAPIRateLimitError):
            loading_bar.inc('tokens')

        else:
            loading_bar.inc('failures')
            loading_bar.print(
                'Failed to call Twitter search. Will retry in %s' % prettyprint_seconds(retry_state.idle_for)
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

        iterator = scraper.search(
            query,
            limit=cli_args.limit,
            before_sleep=before_sleep,
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
