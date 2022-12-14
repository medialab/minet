# =============================================================================
# Minet Instagram User-posts CLI Action
# =============================================================================
#
# Logic of the `instagram user-posts` action.
#
import casanova
from itertools import islice

from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import LoadingBar, die
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_USER_POST_CSV_HEADERS
from minet.instagram.exceptions import (
    InstagramInvalidCookieError,
    InstagramNoPublicationError,
    InstagramPrivateOrNonExistentAccountError,
    InstagramInvalidTargetError,
)


def user_posts_action(cli_args):
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
        add=INSTAGRAM_USER_POST_CSV_HEADERS,
    )

    loading_bar = LoadingBar("Retrieving posts", unit="user", stats={"posts": 0})

    for i, (row, user) in enumerate(enricher.cells(cli_args.column, with_rows=True)):
        loading_bar.update()

        try:
            generator = client.user_posts(user)

            if cli_args.limit:
                generator = islice(generator, cli_args.limit)

            for post in generator:
                enricher.writerow(row, post.as_csv_row())

                loading_bar.inc("posts")

        except InstagramInvalidTargetError:
            loading_bar.print(
                "Given user (line %i) is probably not an Instagram user: %s" % (i, user)
            )
        except InstagramPrivateOrNonExistentAccountError:
            loading_bar.print(
                "Given user (line %i) is probably a private Instagram account or is not an Instagram user: %s"
                % (i, user)
            )

        except InstagramNoPublicationError:
            loading_bar.print(
                "Given user (line %i) has probably no publication: %s" % (i, user)
            )
