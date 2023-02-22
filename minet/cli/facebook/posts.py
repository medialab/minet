# =============================================================================
# Minet Facebook Posts CLI Action
# =============================================================================
#
# Logic of the `fb posts` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.facebook.utils import (
    with_facebook_fatal_errors,
    print_translation_warning_if_needed,
)
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_POST_CSV_HEADERS
from minet.facebook.exceptions import FacebookInvalidTargetError


@with_facebook_fatal_errors
@with_enricher_and_loading_bar(
    headers=FACEBOOK_POST_CSV_HEADERS,
    title="Scraping group posts",
    unit="groups",
    nested=True,
    sub_unit="posts",
)
def action(cli_args, enricher, loading_bar):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    translated_langs = set()

    for i, row, url in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step(url):
            try:
                posts = scraper.posts(url)
            except FacebookInvalidTargetError:
                loading_bar.print(
                    "Given url (line %i) is probably not a Facebook group: %s"
                    % (i, url)
                )
                continue

            for post in posts:
                print_translation_warning_if_needed(loading_bar, translated_langs, post)
                loading_bar.nested_advance()
                enricher.writerow(row, post.as_csv_row())
