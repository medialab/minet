# =============================================================================
# Minet Instagram User-followers CLI Action
# =============================================================================
#
# Logic of the `instagram user-followers` action.
#
from itertools import islice

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_USER_CSV_HEADERS
from minet.instagram.exceptions import (
    InstagramInvalidTargetError,
    InstagramAccountNoFollowError,
    InstagramPrivateAccountError,
)


@with_instagram_fatal_errors
@with_enricher_and_loading_bar(
    headers=INSTAGRAM_USER_CSV_HEADERS,
    title="Scraping followers",
    unit="users",
    nested=True,
    sub_unit="followers",
)
def action(cli_args, enricher, loading_bar):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    for i, row, user in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step(user):
            try:
                generator = client.user_followers(user)

                if cli_args.limit:
                    generator = islice(generator, cli_args.limit)

                for post in generator:
                    enricher.writerow(row, post.as_csv_row())
                    loading_bar.nested_advance()

            except InstagramInvalidTargetError:
                loading_bar.print(
                    "Given user (line %i) is probably not an Instagram user: %s"
                    % (i, user)
                )

            except InstagramAccountNoFollowError:
                loading_bar.print(
                    "Given user (line %i) has probably no follower: %s" % (i, user)
                )

            except InstagramPrivateAccountError as nb_follow:
                loading_bar.print(
                    "Given user (line %i) is probably a private account with %s followers: %s"
                    % (i, nb_follow, user)
                )
