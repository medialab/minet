# =============================================================================
# Minet Twitter Users CLI Action
# =============================================================================
#
# Logic of the `tw users` action.
#
import casanova
from twitwi import normalize_user, format_user_as_csv_row
from twitter import TwitterHTTPError
from twitwi.constants import USER_FIELDS, USER_PARAMS
from ebbe import as_chunks

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient
from minet.cli.twitter.utils import is_not_user_id, is_probably_not_user_screen_name


def twitter_users_action(cli_args):

    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key,
        api_version="2" if cli_args.v2 else "1.1",
    )

    enricher = casanova.enricher(
        cli_args.file, cli_args.output, keep=cli_args.select, add=USER_FIELDS
    )

    loading_bar = LoadingBar(desc="Retrieving users", total=cli_args.total, unit="user")

    def call_client(users):
        kwargs = {}

        if not cli_args.v2:
            if cli_args.ids:
                kwargs["user_id"] = users
            else:
                kwargs["screen_name"] = users

            return client.call(["users", "lookup"], **kwargs)
        else:
            kwargs["params"] = USER_PARAMS
            route = ["users"]

            if cli_args.ids:
                kwargs["ids"] = users
            else:
                kwargs["usernames"] = users
                route = ["users", "by"]

            return client.call(route, **kwargs)

    for chunk in as_chunks(100, enricher.cells(cli_args.column, with_rows=True)):
        users = ",".join(row[1].lstrip("@") for row in chunk)

        for _, user in chunk:
            if cli_args.ids:
                if is_not_user_id(user):
                    loading_bar.die(
                        "The column given as argument doesn't contain user ids, you have probably given user screen names as argument instead. \nTry removing --ids from the command."
                    )

                key = "id"

            else:
                if is_probably_not_user_screen_name(user):
                    loading_bar.die(
                        "The column given as argument probably doesn't contain user screen names, you have probably given user ids as argument instead. \nTry adding --ids to the command."
                    )
                    # force flag to add

                key = "screen_name"

        try:
            result = call_client(users)
        except TwitterHTTPError as e:
            if e.e.code == 404:
                for row, user in chunk:
                    enricher.writerow(row)
            else:
                raise e

            continue

        users_raw_data = result if not cli_args.v2 else result["data"]

        indexed_result = {}

        for user in users_raw_data:
            user = normalize_user(user, v2=cli_args.v2)
            user_row = format_user_as_csv_row(user)
            indexed_result[user[key]] = user_row

        for row, user in chunk:
            user_row = indexed_result.get(user.lstrip("@"))

            enricher.writerow(row, user_row)

        loading_bar.update(len(chunk))
