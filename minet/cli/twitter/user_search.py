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
import casanova
import math
from twitwi import (
    normalize_user,
    format_user_as_csv_row
)
from twitwi.constants import USER_FIELDS

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient

ITEMS_PER_PAGE = 20
MAX_ITEM_COUNT = 1020  # NOTE: API docs say it's 1000, but reality begs to differ
RANGE_UPPER_BOUND = math.ceil(MAX_ITEM_COUNT / ITEMS_PER_PAGE) + 1


def twitter_user_search_action(cli_args):

    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key
    )

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=USER_FIELDS
    )

    loading_bar = LoadingBar(
        desc='Retrieving users',
        total=cli_args.total,
        unit='user'
    )

    for row, query in enricher.cells(cli_args.query, with_rows=True):

        kwargs = {'q': query, 'count': ITEMS_PER_PAGE, 'include_entities': True}

        loading_bar.print('Searching for "%s"' % query)
        loading_bar.inc('queries')

        already_seen_users = set()

        for page in range(1, RANGE_UPPER_BOUND):
            kwargs['page'] = page

            result = client.call(['users', 'search'], **kwargs)
            new_user_count = 0

            for user in result:
                user = normalize_user(user)

                if user['id'] in already_seen_users:
                    continue

                loading_bar.update()

                new_user_count += 1
                already_seen_users.add(user['id'])
                user_row = format_user_as_csv_row(user)
                enricher.writerow(row, user_row)

            # If we did not see a single new user, we can safely stop
            # If the number of results is strictly less than the expected number of
            # items per page, we can safely stop
            if new_user_count == 0 or len(result) < ITEMS_PER_PAGE:
                break
