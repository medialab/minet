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
from ural.facebook import has_facebook_comments

from minet.constants import COOKIE_BROWSERS
from minet.cli.utils import open_output_file, die, edit_namespace_with_csv_io
from minet.facebook.comments import FacebookCommentScraper
from minet.facebook.constants import FACEBOOK_COMMENT_CSV_HEADERS
from minet.facebook.exceptions import FacebookInvalidCookieError


def facebook_comments_action(namespace):

    # Handling output
    output_file = open_output_file(namespace.output)

    # Handling input

    if is_url(namespace.column):
        edit_namespace_with_csv_io(namespace, 'post_url')

    try:
        scraper = FacebookCommentScraper(namespace.cookie)
    except FacebookInvalidCookieError:
        if namespace.cookie in COOKIE_BROWSERS:
            die([
                'Could not extract relevant cookie from "%s".' % namespace.cookie,
                'Note that on Firefox, your Facebook cookie cannot be grabbed if you are',
                'using the "Facebook Container" extension by Mozilla, sorry :('
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

    for i, (row, url) in enumerate(enricher.cells(namespace.column, with_rows=True)):

        if not has_facebook_comments(url):
            tqdm.write('Given url (line %i) probably cannot have Facebook comments: %s' % (i + 1, url), file=sys.stderr)
            continue

        batches = scraper(
            url,
            per_call=True,
            detailed=True,
            format='csv_row'
        )

        for details, batch in batches:
            for comment in batch:
                enricher.writerow(row, comment)

            loading_bar.update(len(batch))
            loading_bar.set_postfix(
                calls=details['calls'],
                replies=details['replies'],
                q=details['queue_size'],
                posts=i + 1
            )

    loading_bar.close()
