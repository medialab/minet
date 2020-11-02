# =============================================================================
# Minet Facebook Url Likes CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving approximate
# likes count by scraping Facebook's like button plugin.
#
import casanova
from tqdm import tqdm

from minet.cli.utils import open_output_file, die

REPORT_HEADERS = ['approx_likes', 'approx_likes_int']


def facebook_url_likes_action(namespace):
    output_file = open_output_file(namespace.output)

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=REPORT_HEADERS
    )

    if namespace.column not in enricher.pos:
        die([
            'Could not find the "%s" column containing the urls in the given CSV file.' % namespace.column
        ])

    loading_bar = tqdm(
        desc='Retrieving likes',
        dynamic_ncols=True,
        unit=' urls',
    )

    for row, url in enricher.cells(namespace.column, with_rows=True):

        loading_bar.update()

        url_data = url.strip()

        enricher.writerow(row)
