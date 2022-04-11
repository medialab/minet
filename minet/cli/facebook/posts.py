# =============================================================================
# Minet Facebook Posts CLI Action
# =============================================================================
#
# Logic of the `fb posts` action.
#
import casanova

from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import die, LoadingBar
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_POST_CSV_HEADERS
from minet.facebook.exceptions import (
    FacebookInvalidCookieError,
    FacebookInvalidTargetError,
)


def facebook_posts_action(cli_args):
    try:
        scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)
    except FacebookInvalidCookieError:
        if cli_args.cookie in COOKIE_BROWSERS:
            die(['Could not extract relevant cookie from "%s".' % cli_args.cookie])

        die(
            [
                "Relevant cookie not found.",
                "A Facebook authentication cookie is necessary to be able to scrape Facebook groups.",
                "Use the --cookie flag to choose a browser from which to extract the cookie or give your cookie directly.",
            ]
        )

    # Enricher
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=FACEBOOK_POST_CSV_HEADERS,
    )

    # Loading bar
    loading_bar = LoadingBar(desc="Scraping posts", unit="post")

    translated_langs = set()

    for i, (row, url) in enumerate(enricher.cells(cli_args.column, with_rows=True), 1):
        loading_bar.inc("groups")

        try:
            posts = scraper.posts(url)
        except FacebookInvalidTargetError:
            loading_bar.print(
                "Given url (line %i) is probably not a Facebook group: %s" % (i, url)
            )
            continue

        for post in posts:
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
