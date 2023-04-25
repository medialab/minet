# =============================================================================
# Minet Twitter Tweet Count CLI Action
# =============================================================================
#
# Logic of the `tw tweet-count` action.
#
from twitter import TwitterHTTPError

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.twitter.utils import validate_query_boundaries, with_twitter_client

ITEMS_PER_PAGE = 100

COUNT_FIELDS = ["tweet_count"]
GRANULARIZED_COUNT_FIELDS = ["start_time", "end_time", "tweet_count"]


def get_headers(cli_args):
    return (
        GRANULARIZED_COUNT_FIELDS if cli_args.granularity is not None else COUNT_FIELDS
    )


@with_enricher_and_loading_bar(
    headers=get_headers, title="Counting tweets", unit="queries"
)
@with_twitter_client(api_version="2")
def action(cli_args, client, enricher, loading_bar):
    validate_query_boundaries(cli_args)

    # Because we are greedy, if --academic is set and no other relevant bound exist,
    # we set --start-time to be the beginning of Twitter
    if (
        cli_args.academic
        and not cli_args.until_id
        and not cli_args.since_id
        and not cli_args.start_time
    ):
        cli_args.start_time = "2006-03-21T00:00:00Z"

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            kwargs = {"query": query}

            if cli_args.start_time:
                kwargs["start_time"] = cli_args.start_time
            if cli_args.end_time:
                kwargs["end_time"] = cli_args.end_time
            if cli_args.since_id:
                kwargs["since_id"] = cli_args.since_id
            if cli_args.until_id:
                kwargs["until_id"] = cli_args.until_id

            kwargs["granularity"] = cli_args.granularity or "day"

            route = (
                ["tweets", "counts", "all"]
                if cli_args.academic
                else ["tweets", "counts", "recent"]
            )

            total_count = 0

            while True:
                try:
                    result = client.call(route, **kwargs)
                except TwitterHTTPError as e:
                    if e.e.code == 404:
                        enricher.writerow(row)
                    else:
                        raise e

                    continue

                for count in result["data"]:
                    total_count += count["tweet_count"]

                    if cli_args.granularity is not None:
                        addendum = [count["start"], count["end"], count["tweet_count"]]
                        enricher.writerow(row, addendum)

                if "next_token" in result["meta"]:
                    kwargs["next_token"] = result["meta"]["next_token"]
                else:
                    break

            if cli_args.granularity is None:
                enricher.writerow(row, [total_count])
