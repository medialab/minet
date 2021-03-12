# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
#
import sys
import casanova
from twitwi.constants import TWEET_FIELDS
from twitwi import format_tweet_as_csv_row

from minet.utils import prettyprint_seconds, PseudoFStringFormatter
from minet.cli.utils import edit_namespace_with_csv_io, LoadingBar
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


def twitter_scrape_action(namespace, output_file):
    single_query = namespace.file is sys.stdin and sys.stdin.isatty()

    if single_query:
        edit_namespace_with_csv_io(namespace, 'query', attr_name='query')

    scraper = TwitterAPIScraper()

    # Stats
    loading_bar = LoadingBar(
        'Collecting tweets',
        total=namespace.limit,
        unit='tweet',
        stats={'tokens': 1, 'queries': 0}
    )

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        add=TWEET_FIELDS + ADDITIONAL_TWEET_FIELDS,
        keep=namespace.select
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

    for row, query in enricher.cells(namespace.query, with_rows=True):

        # Templating?
        if namespace.query_template is not None:
            query = CUSTOM_FORMATTER.format(
                namespace.query_template,
                value=query
            )

        loading_bar.print('Searching for "%s"' % query)
        loading_bar.inc('queries')

        iterator = scraper.search(
            query,
            limit=namespace.limit,
            before_sleep=before_sleep,
            include_referenced_tweets=namespace.include_refs,
            with_meta=True
        )

        try:
            for tweet, meta in iterator:
                loading_bar.update()

                tweet_row = format_tweet_as_csv_row(tweet)
                enricher.writerow(row, tweet_row + format_meta_row(meta))
        except TwitterPublicAPIOverCapacityError:
            loading_bar.die('Got an "Over Capacity" error. Shutting down...')

    loading_bar.close()
