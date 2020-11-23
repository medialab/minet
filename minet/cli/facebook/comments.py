# =============================================================================
# Minet Facebook Comments CLI Action
# =============================================================================
#
# Logic of the `fb comments` action.
#
import casanova
from tqdm import tqdm
from ural import is_url
from ural.facebook import is_facebook_post_url

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
        if namespace.cookie in ['firefox', 'chrome']:
            die('Could not extract cookies from %s.' % namespace.cookie)

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

        if not is_facebook_post_url(url):
            loading_bar.close()
            die('Given url (line %i) is not a Facebook post url: %s' % (i + 1, url))

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
