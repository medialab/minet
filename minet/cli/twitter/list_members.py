# =============================================================================
# Minet Twitter List Members CLI Action
# =============================================================================
#
# Logic of the `tw list-members` action.
#
import re
import casanova
from ebbe import getpath
from twitter import TwitterHTTPError
from twitwi import normalize_user, format_user_as_csv_row
from twitwi.constants import USER_PARAMS, USER_FIELDS
from ural.twitter import parse_twitter_url, TwitterList, TwitterTweet, TwitterUser

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient


ID_RE = re.compile(r"^[0-9]+$")

ITEMS_PER_PAGE = 100


def twitter_list_members_action(cli_args):
    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key,
        api_version="2",
    )

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=USER_FIELDS,
        total=cli_args.total,
    )

    loading_bar = LoadingBar("Retrieving members", total=enricher.total, unit=" users")

    for row, twitter_list in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.inc("lists")

        twitter_id_list = twitter_list

        list_parsed = parse_twitter_url(twitter_list)
        if isinstance(list_parsed, TwitterList):
            twitter_id_list = list_parsed.id
        elif isinstance(list_parsed, (TwitterUser, TwitterTweet)) or (
            not list_parsed and not ID_RE.match(twitter_list)
        ):
            loading_bar.inc("errors")
            loading_bar.print("%s is not a list id or url." % twitter_list)
            continue

        kwargs = {"max_results": ITEMS_PER_PAGE, "params": USER_PARAMS}

        while True:
            try:
                result = client.call(["lists", twitter_id_list, "members"], **kwargs)
            except TwitterHTTPError as e:
                loading_bar.inc("errors")

                if e.e.code == 404:
                    enricher.writerow(row)
                else:
                    raise e

                break

            if result.get("errors"):
                loading_bar.inc("errors")
                loading_bar.print(getpath(result, ["errors", 0, "detail"]))
                break

            if "data" not in result or result["meta"]["result_count"] == 0:
                break

            for user in result["data"]:
                user = normalize_user(user, v2=True)
                user_row = format_user_as_csv_row(user)
                enricher.writerow(row, user_row)
                loading_bar.update()

            if "next_token" in result["meta"]:
                kwargs["pagination_token"] = result["meta"]["next_token"]
            else:
                break
