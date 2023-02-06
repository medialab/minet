# =============================================================================
# Minet Instagram User-infos CLI Action
# =============================================================================
#
# Logic of the `instagram user-infos` action.
#

import casanova

from minet.cli.utils import LoadingBar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_USER_INFO_CSV_HEADERS
from minet.instagram.exceptions import InstagramInvalidTargetError


@with_instagram_fatal_errors
def action(cli_args):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=INSTAGRAM_USER_INFO_CSV_HEADERS,
    )

    loading_bar = LoadingBar("Retrieving infos", unit="user")

    for i, (row, user) in enumerate(enricher.cells(cli_args.column, with_rows=True)):
        loading_bar.update()

        try:
            result = client.user_infos(user)

            enricher.writerow(row, result.as_csv_row())

        except InstagramInvalidTargetError:
            loading_bar.print(
                "Given user (line %i) is probably not an Instagram user: %s" % (i, user)
            )
