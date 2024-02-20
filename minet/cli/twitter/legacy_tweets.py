# =============================================================================
# Minet Twitter Tweets CLI Action
# =============================================================================
#
# Logic of the `tw tweets` action.
#
from twitwi import normalize_tweet, normalize_tweets_payload_v2, format_tweet_as_csv_row
from twitwi.constants import TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_PARAMS
from twitter import TwitterHTTPError
from ebbe import as_chunks

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.twitter.utils import with_twitter_client


@with_enricher_and_loading_bar(
    headers=TWEET_FIELDS, title="Retrieving tweets", unit="tweets"
)
@with_twitter_client()
def action(cli_args, client, enricher, loading_bar):
    def call_client(ids):
        if cli_args.v2:
            kwargs = {
                "ids": ids,
                "expansions": ",".join(TWEET_EXPANSIONS),
                "params": TWEET_PARAMS,
            }
            return client.call(["tweets"], **kwargs)
        else:
            kwargs = {"_id": ids, "tweet_mode": "extended"}
            return client.call(["statuses", "lookup"], **kwargs)

    for chunk in as_chunks(100, enricher.cells(cli_args.column, with_rows=True)):
        tweets = ",".join(row[1] for row in chunk)

        with loading_bar.step(count=len(chunk)):
            try:
                result = call_client(tweets)
            except TwitterHTTPError as e:
                if e.e.code == 404:
                    for row, tweet in chunk:
                        enricher.writerow(row)
                else:
                    raise e

                continue

            indexed_result = {}

            if cli_args.v2:
                normalized_tweets = normalize_tweets_payload_v2(
                    result, locale=cli_args.timezone, collection_source="api"
                )
                for normalized_tweet in normalized_tweets:
                    addendum = format_tweet_as_csv_row(normalized_tweet)
                    indexed_result[normalized_tweet["id"]] = addendum

            else:
                for tweet in result:
                    tweet = normalize_tweet(
                        tweet, locale=cli_args.timezone, collection_source="api"
                    )
                    addendum = format_tweet_as_csv_row(tweet)
                    indexed_result[tweet["id"]] = addendum

            for row, tweet in chunk:
                addendum = indexed_result.get(tweet)
                enricher.writerow(row, addendum)
