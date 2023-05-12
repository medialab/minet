# =============================================================================
# Minet Twitter User Search CLI Action
# =============================================================================
#
# Logic of the `tw user-search` action using API v1 to search users using the
# given query.
#
# Note that the API docs are a bit fuzzy on the matter as it seems that there
# is no good way to handle pagination. As it seems, the last page actually
# still return a maximum number of items, even if it means returning users
# that were already seen, again. Hence the not-straigtforward-looking code
# below to handle pagination in spite of the API's shortcomings.
#
import math
from twitwi import normalize_user, format_user_as_csv_row
from twitwi.constants import USER_FIELDS

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.twitter.utils import with_twitter_client

ITEMS_PER_PAGE = 20
MAX_ITEM_COUNT = 1020  # NOTE: API docs say it's 1000, but reality begs to differ
RANGE_UPPER_BOUND = math.ceil(MAX_ITEM_COUNT / ITEMS_PER_PAGE) + 1


@with_enricher_and_loading_bar(
    headers=USER_FIELDS,
    title="Searching users",
    unit="queries",
    nested=True,
    sub_unit="users",
)
@with_twitter_client()
def action(cli_args, client, enricher, loading_bar):
    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query):
            kwargs = {"q": query, "count": ITEMS_PER_PAGE, "include_entities": True}

            already_seen_users = set()

            for page in range(1, RANGE_UPPER_BOUND):
                kwargs["page"] = page

                result = client.call(["users", "search"], **kwargs)
                new_user_count = 0

                for user in result:
                    user = normalize_user(user, locale=cli_args.timezone)

                    if user["id"] in already_seen_users:
                        continue

                    loading_bar.nested_advance()

                    new_user_count += 1
                    already_seen_users.add(user["id"])
                    user_row = format_user_as_csv_row(user)
                    enricher.writerow(row, user_row)

                # If we did not see a single new user, we can safely stop
                # If the number of results is strictly less than the expected number of
                # items per page, we can safely stop
                if new_user_count == 0 or len(result) < ITEMS_PER_PAGE:
                    break
