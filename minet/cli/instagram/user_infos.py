# =============================================================================
# Minet Instagram User-infos CLI Action
# =============================================================================
#
# Logic of the `instagram user-infos` action.
#

import casanova

from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import LoadingBar, die
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_USER_INFO_CSV_HEADERS
from minet.instagram.exceptions import (
    InstagramInvalidTargetError,
    InstagramInvalidCookieError,
)


def user_infos_action(cli_args):
    try:
        client = InstagramAPIScraper(cookie=cli_args.cookie)
    except InstagramInvalidCookieError:
        if cli_args.cookie in COOKIE_BROWSERS:
            die(['Could not extract relevant cookie from "%s".' % cli_args.cookie])

        die(
            [
                "Relevant cookie not found.",
                "A Facebook authentication cookie is necessary to be able to scrape Instagram.",
                "Use the --cookie flag to choose a browser from which to extract the cookie or give your cookie directly.",
            ]
        )

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
