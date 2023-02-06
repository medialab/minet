# =============================================================================
# Minet Instagram User-followings CLI Action
# =============================================================================
#
# Logic of the `instagram user-followings` action.
#

import casanova
from itertools import islice

from minet.cli.utils import LoadingBar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_USER_CSV_HEADERS
from minet.instagram.exceptions import (
    InstagramInvalidTargetError,
    InstagramPrivateAccountError,
    InstagramAccountNoFollowError,
)


@with_instagram_fatal_errors
def action(cli_args):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=INSTAGRAM_USER_CSV_HEADERS,
    )

    loading_bar = LoadingBar(
        "Retrieving followings", unit="user", stats={"followings": 0}
    )

    for i, (row, user) in enumerate(enricher.cells(cli_args.column, with_rows=True)):
        loading_bar.update()

        try:
            generator = client.user_following(user)

            if cli_args.limit:
                generator = islice(generator, cli_args.limit)

            for post in generator:
                enricher.writerow(row, post.as_csv_row())

                loading_bar.inc("followings")

        except InstagramInvalidTargetError:
            loading_bar.print(
                "Given user (line %i) is probably not an Instagram user: %s" % (i, user)
            )

        except InstagramAccountNoFollowError:
            loading_bar.print(
                "Given user (line %i) probably doesn't follow any account: %s"
                % (i, user)
            )

        except InstagramPrivateAccountError as nb_follow:
            loading_bar.print(
                "Given user (line %i) is probably a private account following %s accounts: %s"
                % (i, nb_follow, user)
            )
