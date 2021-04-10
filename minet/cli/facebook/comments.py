# =============================================================================
# Minet Facebook Comments CLI Action
# =============================================================================
#
# Logic of the `fb comments` action.
#
import casanova
import tqdm
import sys
from ural import is_url

from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import open_output_file, die, edit_cli_args_with_csv_io, LoadingBar
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_COMMENT_CSV_HEADERS
from minet.facebook.exceptions import (
    FacebookInvalidCookieError,
    FacebookInvalidTargetError
)


def facebook_comments_action(cli_args):

    # Handling output
    output_file = open_output_file(cli_args.output)

    # Handling input
    if is_url(cli_args.column):
        edit_cli_args_with_csv_io(cli_args, 'post_url')

    try:
        scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)
    except FacebookInvalidCookieError:
        if cli_args.cookie in COOKIE_BROWSERS:
            die([
                'Could not extract relevant cookie from "%s".' % cli_args.cookie
            ])

        die([
            'Relevant cookie not found.',
            'A Facebook authentication cookie is necessary to be able to access Facebook post comments.',
            'Use the --cookie flag to choose a browser from which to extract the cookie or give your cookie directly.'
        ])

    # Enricher
    enricher = casanova.enricher(
        cli_args.file,
        output_file,
        keep=cli_args.select,
        add=FACEBOOK_COMMENT_CSV_HEADERS
    )

    # Loading bar
    loading_bar = LoadingBar(
        desc='Scraping comments',
        unit='comment'
    )

    for i, (row, url) in enumerate(enricher.cells(cli_args.column, with_rows=True), 1):
        try:
            batches = scraper.comments(
                url,
                per_call=True,
                detailed=True
            )
        except FacebookInvalidTargetError:
            tqdm.write('Given url (line %i) is probably not a Facebook resource having comments: %s' % (i, url), file=sys.stderr)
            continue

        for details, batch in batches:
            for comment in batch:
                enricher.writerow(row, comment.as_csv_row())

            loading_bar.update(len(batch))
            loading_bar.update_stats(
                calls=details['calls'],
                replies=details['replies'],
                q=details['queue_size'],
                posts=i
            )

    loading_bar.close()
