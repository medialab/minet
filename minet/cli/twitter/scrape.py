# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
import sys
import casanova
from tqdm import tqdm
from twitwi.constants import TWEET_FIELDS
from twitwi import format_tweet_as_csv_row

from minet.utils import prettyprint_seconds, PseudoFStringFormatter
from minet.cli.utils import edit_namespace_with_csv_io
from minet.twitter import TwitterAPIScraper
from minet.twitter.exceptions import TwitterPublicAPIRateLimitError

CUSTOM_FORMATTER = PseudoFStringFormatter()


def twitter_scrape_action(namespace, output_file):
    single_query = namespace.file is sys.stdin and sys.stdin.isatty()

    if single_query:
        edit_namespace_with_csv_io(namespace, 'query', attr_name='query')

    scraper = TwitterAPIScraper()

    # Stats
    tokens = 1
    failures = 0
    queries = 0

    loading_bar = tqdm(
        desc='Collecting tweets',
        dynamic_ncols=True,
        total=namespace.limit,
        unit=' tweet',
        postfix={'tokens': tokens, 'queries': queries}
    )

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        add=TWEET_FIELDS,
        keep=namespace.select
    )

    def before_sleep(retry_state):
        nonlocal tokens
        nonlocal failures

        exc = retry_state.outcome.exception()

        if isinstance(exc, TwitterPublicAPIRateLimitError):
            tokens += 1
            loading_bar.set_postfix(tokens=tokens)

        else:
            failures += 1
            loading_bar.set_postfix(failures=failures)
            loading_bar.write(
                'Failed to call Twitter search. Will retry in %s' % prettyprint_seconds(retry_state.idle_for),
                file=sys.stderr
            )

    for row, query in enricher.cells(namespace.query, with_rows=True):

        # Templating?
        if namespace.query_template is not None:
            query = CUSTOM_FORMATTER.format(
                namespace.query_template,
                value=query
            )

        loading_bar.write('Searching for "%s"' % query, file=sys.stderr)
        queries += 1

        loading_bar.set_postfix(queries=queries)

        iterator = scraper.search(
            query,
            limit=namespace.limit,
            before_sleep=before_sleep,
            include_referenced_tweets=namespace.include_refs
        )

        for tweet in iterator:
            loading_bar.update()

            tweet_row = format_tweet_as_csv_row(tweet)
            enricher.writerow(row, tweet_row)

    loading_bar.close()
