# =============================================================================
# Minet Facebook Post CLI Action
# =============================================================================
#
# Logic of the `fb post` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.facebook.utils import with_facebook_fatal_errors
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
            if post.translated_text and post.translated_from not in translated_langs:
                translated_langs.add(post.translated_from)
                lines = [
                    "[warning]Found text translated from %s![/warning]"
                    % post.translated_from,
                    "Since it means original text may not be entirely retrieved you might want",
                    'to edit your Facebook language settings to add "%s" to'
                    % post.translated_from,
                    'the "Languages you don\'t want to be offered translations for" list here:',
                    "https://www.facebook.com/settings/?tab=language",
                    "",
                ]

                loading_bar.print(lines)

            enricher.writerow(row, post.as_csv_row())
