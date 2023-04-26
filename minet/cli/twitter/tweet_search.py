# =============================================================================
# Minet Twitter Tweet Search CLI Action
# =============================================================================
#
# Logic of the `tw tweet-search` action.
#
from twitwi import normalize_tweets_payload_v2, format_tweet_as_csv_row
from twitwi.constants import TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_PARAMS
from twitter import TwitterHTTPError

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.twitter.utils import with_twitter_client
from minet.cli.twitter.utils import validate_query_boundaries


@with_enricher_and_loading_bar(
    headers=TWEET_FIELDS,
    title="Retrieving tweets",
    unit="queries",
    nested=True,
    sub_unit="tweets",
)
@with_twitter_client(api_version="2")
def action(cli_args, client, enricher, loading_bar):
    validate_query_boundaries(cli_args)

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query):
            kwargs = {
                "query": query,
                "max_results": 500 if cli_args.academic else 100,
                "sort_order": cli_args.sort_order,
                "expansions": ",".join(TWEET_EXPANSIONS),
                "params": TWEET_PARAMS,
            }

            if cli_args.start_time:
                kwargs["start_time"] = cli_args.start_time
            if cli_args.end_time:
                kwargs["end_time"] = cli_args.end_time
            if cli_args.since_id:
                kwargs["since_id"] = cli_args.since_id
            if cli_args.until_id:
                kwargs["until_id"] = cli_args.until_id

            route = (
                ["tweets", "search", "all"]
                if cli_args.academic
                else ["tweets", "search", "recent"]
            )

            while True:
                try:
                    result = client.call(route, **kwargs)
                except TwitterHTTPError as e:
                    if e.e.code == 404:
                        enricher.writerow(row)
                    else:
                        raise e

                    continue

                # Empty response
                if (
                    result["meta"]["result_count"] == 0
                    and "next_token" in result["meta"]
                ):
                    kwargs["next_token"] = result["meta"]["next_token"]
                    continue

                normalized_tweets = normalize_tweets_payload_v2(
                    result, locale=cli_args.timezone, collection_source="api"
                )

                for normalized_tweet in normalized_tweets:
                    addendum = format_tweet_as_csv_row(normalized_tweet)
                    enricher.writerow(row, addendum)
                    loading_bar.nested_advance()

                if "next_token" in result["meta"]:
                    kwargs["next_token"] = result["meta"]["next_token"]
                else:
                    break
