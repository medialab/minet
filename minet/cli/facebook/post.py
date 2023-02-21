# =============================================================================
# Minet Facebook Post CLI Action
# =============================================================================
#
# Logic of the `fb post` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.facebook.utils import (
    with_facebook_fatal_errors,
    print_translation_warning_if_needed,
)
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import (
    FACEBOOK_POST_WITH_REACTIONS_CSV_HEADERS,
)
from minet.facebook.exceptions import (
    FacebookInvalidTargetError,
    FacebookNotPostError,
    FacebookWatchError,
)

CATCH = {
    FacebookInvalidTargetError: "Url is not available (link broken, private content, content removed, or scraping error): [info]{item}[/info]",
    FacebookNotPostError: "Url is not a post (may be an incorrect url): [info]{item}[/info]",
    FacebookWatchError: "Url leads to Facebook Watch and cannot be processed: [info]{item}[/info]",
}


@with_facebook_fatal_errors
@with_enricher_and_loading_bar(
    headers=FACEBOOK_POST_WITH_REACTIONS_CSV_HEADERS,
    title="Scraping posts",
    unit="posts",
)
def action(cli_args, enricher, loading_bar):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    translated_langs = set()

    for i, row, url in enricher.enumerate_cells(cli_args.column, with_rows=True):
        with loading_bar.step(url, index=i, catch=CATCH):
            post = scraper.post(url)
            print_translation_warning_if_needed(loading_bar, translated_langs, post)
            enricher.writerow(row, post.as_csv_row())
