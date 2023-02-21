# =============================================================================
# Minet Facebook Posts CLI Action
# =============================================================================
#
# Logic of the `fb posts` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.facebook.utils import with_facebook_fatal_errors
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

    for i, (row, url) in enumerate(enricher.cells(cli_args.column, with_rows=True), 1):
        with loading_bar.tick(url):
            try:
                posts = scraper.posts(url)
            except FacebookInvalidTargetError:
                loading_bar.print(
                    "Given url (line %i) is probably not a Facebook group: %s"
                    % (i, url)
                )
                continue

            for post in posts:
                if (
                    post.translated_text
                    and post.translated_from not in translated_langs
                ):
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

                loading_bar.nested_advance()
                enricher.writerow(row, post.as_csv_row())
