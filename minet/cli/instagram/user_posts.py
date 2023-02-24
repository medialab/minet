# =============================================================================
# Minet Instagram User-posts CLI Action
# =============================================================================
#
# Logic of the `instagram user-posts` action.
#
from itertools import islice

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_POST_CSV_HEADERS
from minet.instagram.exceptions import (
    InstagramNoPublicationError,
    InstagramPrivateOrNonExistentAccountError,
    InstagramInvalidTargetError,
)


@with_instagram_fatal_errors
@with_enricher_and_loading_bar(
    headers=INSTAGRAM_POST_CSV_HEADERS,
    title="Scraping posts",
    unit="users",
    nested=True,
    sub_unit="posts",
)
def action(cli_args, enricher, loading_bar):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    for i, row, user in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step(user):
            try:
                generator = client.user_posts(user)

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

            except InstagramPrivateOrNonExistentAccountError:
                loading_bar.print(
                    "Given user (line %i) is probably a private Instagram account or is not an Instagram user: %s"
                    % (i, user)
                )

            except InstagramNoPublicationError:
                loading_bar.print(
                    "Given user (line %i) has probably no publication: %s" % (i, user)
                )
