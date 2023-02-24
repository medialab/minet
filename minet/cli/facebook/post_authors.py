# =============================================================================
# Minet Facebook Post Authors CLI Action
# =============================================================================
#
# Logic of the `fb post-authors` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.facebook.utils import with_facebook_fatal_errors
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_USER_CSV_HEADERS
from minet.facebook.exceptions import FacebookInvalidTargetError


@with_facebook_fatal_errors
@with_enricher_and_loading_bar(
    headers=FACEBOOK_USER_CSV_HEADERS, title="Finding authors", unit="posts"
)
def action(cli_args, enricher, loading_bar):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    for i, row, post_url in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step():
            try:
                author = scraper.post_author(post_url)
            except FacebookInvalidTargetError:
                loading_bar.print(
                    "Given url (line %i) is probably not a Facebook group post: %s"
                    % (i, post_url)
                )
                continue

            enricher.writerow(row, author.as_csv_row() if author is not None else None)
