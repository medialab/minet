# =============================================================================
# Minet CrowdTangle Posts By Id CLI Action
# =============================================================================
#
# Logic of the `ct posts-by-id` action.
#
import casanova
from tqdm import tqdm
from ural import ensure_protocol

import minet.facebook as facebook
from minet.cli.utils import die
from minet.crowdtangle.constants import CROWDTANGLE_POST_CSV_HEADERS
from minet.crowdtangle.client import CrowdTangleClient
from minet.crowdtangle.exceptions import CrowdTangleInvalidTokenError


def crowdtangle_posts_by_id_action(namespace, output_file):

    client = CrowdTangleClient(namespace.token, rate_limit=namespace.rate_limit)

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=CROWDTANGLE_POST_CSV_HEADERS
    )

    loading_bar = tqdm(
        desc='Retrieving posts',
        dynamic_ncols=True,
        total=namespace.total,
        unit=' posts'
    )

    try:
        for row, url in enricher.cells(namespace.column, with_rows=True):
            loading_bar.update()

            url = ensure_protocol(url)

            post_id = facebook.post_id_from_url(url)
            print(post_id)
            die('Stopping for now!')

            if post_id is None:
                enricher.writerow(row)
                continue

            post = client.post(post_id, format='csv_row')

            print(post)
            break

    except CrowdTangleInvalidTokenError:
        die([
            'Your API token is invalid.',
            'Check that you indicated a valid one using the `--token` argument.'
        ])
