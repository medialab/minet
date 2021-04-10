# =============================================================================
# Minet Facebook Comments CLI Action
# =============================================================================
#
# Logic of the `fb comments` action.
#
import casanova
import tqdm
import sys
from tqdm import tqdm
from ural import is_url

from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import open_output_file, die, edit_namespace_with_csv_io
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_COMMENT_CSV_HEADERS
from minet.facebook.exceptions import (
    FacebookInvalidCookieError,
    FacebookInvalidTargetError
)


def facebook_comments_action(namespace):

    # Handling output
    output_file = open_output_file(namespace.output)

    # Handling input
    if is_url(namespace.column):
        edit_namespace_with_csv_io(namespace, 'post_url')

    try:
        scraper = FacebookMobileScraper(namespace.cookie, throttle=namespace.throttle)
    except FacebookInvalidCookieError:
        if namespace.cookie in COOKIE_BROWSERS:
            die([
                'Could not extract relevant cookie from "%s".' % namespace.cookie
            ])

        die([
            'Relevant cookie not found.',
            'A Facebook authentication cookie is necessary to be able to access Facebook post comments.',
            'Use the --cookie flag to choose a browser from which to extract the cookie or give your cookie directly.'
        ])

    # Enricher
    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=FACEBOOK_COMMENT_CSV_HEADERS
    )

    # Loading bar
    loading_bar = tqdm(
        desc='Scraping comments',
        dynamic_ncols=True,
        unit=' comments'
    )

    for i, (row, url) in enumerate(enricher.cells(namespace.column, with_rows=True), 1):
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
            loading_bar.set_postfix(
                calls=details['calls'],
                replies=details['replies'],
                q=details['queue_size'],
                posts=i
            )

    loading_bar.close()
