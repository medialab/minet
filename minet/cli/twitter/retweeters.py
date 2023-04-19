# =============================================================================
# Minet Twitter Retweeters CLI Action
# =============================================================================
#
# Logic of the `tw retweeters` action.
#
import re
from ebbe import getpath
from twitter import TwitterHTTPError
from twitwi import normalize_user, format_user_as_csv_row
from twitwi.constants import USER_PARAMS, USER_FIELDS
from ural.twitter import parse_twitter_url, TwitterTweet, TwitterUser, TwitterList

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.twitter.utils import with_twitter_client

ID_RE = re.compile(r"^[0-9]+$")

ITEMS_PER_PAGE = 100


@with_enricher_and_loading_bar(
    headers=USER_FIELDS,
    title="Retrieving retweeters",
    unit="tweets",
    nested=True,
    sub_unit="retweeters",
)
@with_twitter_client(api_version="2")
def action(cli_args, client, enricher, loading_bar):
    for row, tweet in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(tweet):
            tweet_id = tweet

            tweet_parsed = parse_twitter_url(tweet)
            if isinstance(tweet_parsed, TwitterTweet):
                tweet_id = tweet_parsed.id
            elif isinstance(tweet_parsed, (TwitterUser, TwitterList)) or (
                not tweet_parsed and not ID_RE.match(tweet)
            ):
                loading_bar.print("%s is not a tweet id or url." % tweet)
                continue

            kwargs = {"max_results": ITEMS_PER_PAGE, "params": USER_PARAMS}

            while True:
                try:
                    result = client.call(["tweets", tweet_id, "retweeted_by"], **kwargs)
                except TwitterHTTPError as e:
                    if e.e.code == 404:
                        enricher.writerow(row)
                    else:
                        raise e

                    break

                if result.get("errors"):
                    loading_bar.print(getpath(result, ["errors", 0, "detail"]))
                    break

                if "data" not in result or result["meta"]["result_count"] == 0:
                    break

                for user in result["data"]:
                    user = normalize_user(user, locale=cli_args.timezone, v2=True)
                    user_row = format_user_as_csv_row(user)
                    enricher.writerow(row, user_row)
                    loading_bar.nested_advance()

                if "next_token" in result["meta"]:
                    kwargs["pagination_token"] = result["meta"]["next_token"]
                else:
                    break
