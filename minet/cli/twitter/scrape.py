# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
import csv
from tqdm import tqdm
from twitwi.constants import TWEET_FIELDS
from twitwi import transform_tweet_into_csv_dict

from minet.twitter import TwitterAPIScraper
from minet.twitter.exceptions import (
    TwitterPublicAPIRateLimitError,
    TwitterPublicAPIInvalidResponseError
)


def twitter_scrape_action(namespace, output_file):
    scraper = TwitterAPIScraper()

    # Stats
    tokens = 1
    failures = 0

    loading_bar = tqdm(
        desc='Collecting tweets',
        dynamic_ncols=True,
        total=namespace.limit,
        unit=' tweet',
        postfix={'tokens': tokens}
    )

    writer = csv.DictWriter(
        output_file,
        fieldnames=TWEET_FIELDS,
        extrasaction='ignore'
    )
    writer.writeheader()

    def before_sleep(retry_state):
        nonlocal tokens
        nonlocal failures

        exc = retry_state.outcome.exception()

        if isinstance(exc, TwitterPublicAPIRateLimitError):
            tokens += 1
            loading_bar.set_postfix(tokens=tokens)

        elif isinstance(exc, TwitterPublicAPIInvalidResponseError):
            failures += 1
            loading_bar.set_postfix(failures=failures)

    iterator = scraper.search(
        namespace.query,
        limit=namespace.limit,
        before_sleep=before_sleep,
        include_referenced_tweets=namespace.include_refs
    )

    for tweet in iterator:
        loading_bar.update()

        transform_tweet_into_csv_dict(tweet)
        writer.writerow(tweet)

    loading_bar.close()
