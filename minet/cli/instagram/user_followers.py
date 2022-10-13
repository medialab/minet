# =============================================================================
# Minet Instagram User-followers CLI Action
# =============================================================================
#
# Logic of the `instagram user-followers` action.
#

import casanova
from itertools import islice

from minet.cli.utils import LoadingBar
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_USER_FOLLOW_CSV_HEADERS


def user_followers_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=INSTAGRAM_USER_FOLLOW_CSV_HEADERS,
    )

    loading_bar = LoadingBar(
        "Retrieving followers", unit="user", stats={"followers": 0}
    )

    client = InstagramAPIScraper(cookie=cli_args.cookie)
    for row, user in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        generator = client.user_followers(user)

        if cli_args.limit:
            generator = islice(generator, cli_args.limit)

        for post in generator:
            enricher.writerow(row, post.as_csv_row())

            loading_bar.inc("followers")
