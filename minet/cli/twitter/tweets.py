# =============================================================================
# Minet Twitter Tweets CLI Action
# =============================================================================
#
# Logic of the `tw tweets` action.
#
import casanova
from twitwi import normalize_tweet, normalize_tweets_payload_v2, format_tweet_as_csv_row
from twitwi.constants import TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_PARAMS
from twitter import TwitterHTTPError
from ebbe import as_chunks

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient


def twitter_tweets_action(cli_args):

    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key,
        api_version="2" if cli_args.v2 else "1.1",
    )

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=TWEET_FIELDS,
        total=cli_args.total,
    )

    loading_bar = LoadingBar(
        "Retrieving tweets metadata", total=enricher.total, unit="tweet"
    )

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

        try:
            result = call_client(tweets)
        except TwitterHTTPError as e:
            loading_bar.inc("errors")

            if e.e.code == 404:
                for row, tweet in chunk:
                    enricher.writerow(row)
            else:
                raise e

            continue

        indexed_result = {}

        if cli_args.v2:
            normalized_tweets = normalize_tweets_payload_v2(
                result, collection_source="api"
            )
            for normalized_tweet in normalized_tweets:
                addendum = format_tweet_as_csv_row(normalized_tweet)
                indexed_result[normalized_tweet["id"]] = addendum

        else:
            for tweet in result:
                tweet = normalize_tweet(tweet, collection_source="api")
                addendum = format_tweet_as_csv_row(tweet)
                indexed_result[tweet["id"]] = addendum

        for row, tweet in chunk:
            addendum = indexed_result.get(tweet)

            enricher.writerow(row, addendum)

        loading_bar.update(len(chunk))
