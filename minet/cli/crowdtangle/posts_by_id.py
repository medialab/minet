# =============================================================================
# Minet CrowdTangle Posts By Id CLI Action
# =============================================================================
#
# Logic of the `ct posts-by-id` action.
#
import casanova
from ural import ensure_protocol
from ural.facebook import is_facebook_post_url

import minet.facebook as facebook
from minet.cli.utils import LoadingBar
from minet.crowdtangle.constants import CROWDTANGLE_POST_CSV_HEADERS
from minet.crowdtangle.client import CrowdTangleAPIClient
from minet.crowdtangle.exceptions import (
    CrowdTangleInvalidTokenError,
    CrowdTanglePostNotFound,
)


def crowdtangle_posts_by_id_action(cli_args):

    client = CrowdTangleAPIClient(cli_args.token, rate_limit=cli_args.rate_limit)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=CROWDTANGLE_POST_CSV_HEADERS,
    )

    loading_bar = LoadingBar(desc="Retrieving posts", total=cli_args.total, unit="post")

    try:
        for row, url in enricher.cells(cli_args.column, with_rows=True):
            loading_bar.update()

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

            try:
                post = client.post(post_id)
                enricher.writerow(row, post.as_csv_row())
            except CrowdTanglePostNotFound as error:
                enricher.writerow(row)
                loading_bar.print(
                    "\n\n"
                    "CrowdTangle does not have data about the post at this url: {url}\n"
                    "The CrowdTangle API's response is: \n{data}\n".format(
                        url=url, data=error.data
                    )
                )

    except CrowdTangleInvalidTokenError:
        loading_bar.die(
            [
                "Your API token is invalid.",
                "Check that you indicated a valid one using the `--token` argument.",
            ]
        )
