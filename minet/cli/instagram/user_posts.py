# =============================================================================
# Minet Instagram User-posts CLI Action
# =============================================================================
#
# Logic of the `instagram user-posts` action.
#
import casanova
from itertools import islice

from minet.cli.utils import LoadingBar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_USER_POST_CSV_HEADERS
from minet.instagram.exceptions import (
    InstagramNoPublicationError,
    InstagramPrivateOrNonExistentAccountError,
    InstagramInvalidTargetError,
)


@with_instagram_fatal_errors
def action(cli_args):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

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
