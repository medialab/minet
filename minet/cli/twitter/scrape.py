# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
import csv
from tqdm import tqdm
from twitwi.constants import TWEET_FIELDS
from twitwi.formatters import transform_tweet_into_csv_dict

from minet.twitter import TwitterAPIScraper


def twitter_scrape_action(namespace, output_file):
    scraper = TwitterAPIScraper()

    loading_bar = tqdm(
        desc='Collecting tweets',
        dynamic_ncols=True,
        total=namespace.limit,
        unit=' tweet'
    )

    writer = csv.DictWriter(
        output_file,
        fieldnames=TWEET_FIELDS,
        extrasaction='ignore'
    )
    writer.writeheader()

    for tweet in scraper.search(namespace.query, limit=namespace.limit):
        loading_bar.update()

        transform_tweet_into_csv_dict(tweet)
        writer.writerow(tweet)

    loading_bar.close()
