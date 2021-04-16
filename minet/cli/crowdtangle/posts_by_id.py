# =============================================================================
# Minet CrowdTangle Posts By Id CLI Action
# =============================================================================
#
# Logic of the `ct posts-by-id` action.
#
import casanova
from tqdm import tqdm
from ural import ensure_protocol
from ural.facebook import is_facebook_post_url

import minet.facebook as facebook
from minet.cli.utils import die
from minet.crowdtangle.constants import CROWDTANGLE_POST_CSV_HEADERS
from minet.crowdtangle.client import CrowdTangleAPIClient
from minet.crowdtangle.exceptions import CrowdTangleInvalidTokenError


def crowdtangle_posts_by_id_action(cli_args, output_file):

    client = CrowdTangleAPIClient(cli_args.token, rate_limit=cli_args.rate_limit)

    already_done = 0

    def listener(event, row):
        nonlocal already_done

        if event == 'resume.input':
            already_done += 1

    enricher = casanova.enricher(
        cli_args.file,
        output_file,
        keep=cli_args.select,
        add=CROWDTANGLE_POST_CSV_HEADERS,
        resumable=cli_args.resume,
        listener=listener
    )

    loading_bar = tqdm(
        desc='Retrieving posts',
        dynamic_ncols=True,
        total=cli_args.total,
        unit=' posts'
    )

    loading_bar.update(already_done)

    try:
        for row, url in enricher.cells(cli_args.column, with_rows=True):
            with loading_bar:
                url = url.strip()

                if not url:
                    enricher.writerow(row)
                    continue

                url = ensure_protocol(url)

                if not is_facebook_post_url(url):
                    enricher.writerow(row)
                    continue

                post_id = facebook.post_id_from_url(url)

                if post_id is None:
                    enricher.writerow(row)
                    continue

                post = client.post(post_id)
                enricher.writerow(row, post)

    except CrowdTangleInvalidTokenError:
        die([
            'Your API token is invalid.',
            'Check that you indicated a valid one using the `--token` argument.'
        ])
