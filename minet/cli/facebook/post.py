# =============================================================================
# Minet Facebook Post CLI Action
# =============================================================================
#
# Logic of the `fb post` action.
#
import casanova

from minet.cli.utils import LoadingBar
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


@with_facebook_fatal_errors
def action(cli_args):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    # Enricher
    enricher = casanova.enricher(
        cli_args.input,
        cli_args.output,
        keep=cli_args.select,
        add=FACEBOOK_POST_WITH_REACTIONS_CSV_HEADERS,
    )

    # Loading bar
    loading_bar = LoadingBar(desc="Scraping posts", unit="post")

    translated_langs = set()

    for i, (row, url) in enumerate(enricher.cells(cli_args.column, with_rows=True), 1):
        loading_bar.inc("posts")

        try:
            post = scraper.post(url)
            if post.translated_text and post.translated_from not in translated_langs:
                translated_langs.add(post.translated_from)
                lines = [
                    "Found text translated from %s!" % post.translated_from,
                    "Since it means original text may not be entirely retrieved you might want",
                    'to edit your Facebook language settings to add "%s" to'
                    % post.translated_from,
                    'the "Languages you don\'t want to be offered translations for" list here:',
                    "https://www.facebook.com/settings/?tab=language",
                ]

                for line in lines:
                    loading_bar.print(line)

                loading_bar.print()

            loading_bar.update()
            enricher.writerow(row, post.as_csv_row())
        except FacebookInvalidTargetError:
            loading_bar.print(
                "Given url (line %i) is not available (link broken, private content, content removed, or scraping error): %s"
                % (i, url)
            )
        except FacebookNotPostError:
            loading_bar.print(
                "Given url (line %i) is not a post (may be an incorrect url): %s"
                % (i, url)
            )
        except FacebookWatchError:
            loading_bar.print(
                "Given url (line %i) leads to Facebook Watch: %s" % (i, url)
            )
