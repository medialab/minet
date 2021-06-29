# =============================================================================
# Minet Facebook Post Authors CLI Action
# =============================================================================
#
# Logic of the `fb post-authors` action.
#
import casanova

from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import die, LoadingBar
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_USER_CSV_HEADERS
from minet.facebook.exceptions import (
    FacebookInvalidCookieError,
    FacebookInvalidTargetError
)


def facebook_post_authors_action(cli_args):
    try:
        scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)
    except FacebookInvalidCookieError:
        if cli_args.cookie in COOKIE_BROWSERS:
            die([
                'Could not extract relevant cookie from "%s".' % cli_args.cookie
            ])

        die([
            'Relevant cookie not found.',
            'A Facebook authentication cookie is necessary to be able to scrape Facebook comments.',
            'Use the --cookie flag to choose a browser from which to extract the cookie or give your cookie directly.'
        ])

    # Enricher
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=FACEBOOK_USER_CSV_HEADERS
    )

    # Loading bar
    loading_bar = LoadingBar(
        desc='Finding authors',
        unit='post'
    )

    for i, (row, post_url) in enumerate(enricher.cells(cli_args.column, with_rows=True), 1):
        loading_bar.update()

        try:
            author = scraper.post_author(post_url)
        except FacebookInvalidTargetError:
            loading_bar.print('Given url (line %i) is probably not a Facebook group post: %s' % (i, post_url))
            continue

        enricher.writerow(row, author.as_csv_row() if author is not None else None)
