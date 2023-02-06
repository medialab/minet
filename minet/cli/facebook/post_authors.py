# =============================================================================
# Minet Facebook Post Authors CLI Action
# =============================================================================
#
# Logic of the `fb post-authors` action.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.cli.facebook.utils import with_facebook_fatal_errors
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_USER_CSV_HEADERS
from minet.facebook.exceptions import FacebookInvalidTargetError


@with_facebook_fatal_errors
def action(cli_args):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    # Enricher
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=FACEBOOK_USER_CSV_HEADERS,
    )

    # Loading bar
    loading_bar = LoadingBar(desc="Finding authors", unit="post")

    for i, (row, post_url) in enumerate(
        enricher.cells(cli_args.column, with_rows=True), 1
    ):
        loading_bar.update()

        try:
            author = scraper.post_author(post_url)
        except FacebookInvalidTargetError:
            loading_bar.print(
                "Given url (line %i) is probably not a Facebook group post: %s"
                % (i, post_url)
            )
            continue

        enricher.writerow(row, author.as_csv_row() if author is not None else None)
