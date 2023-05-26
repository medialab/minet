# =============================================================================
# Minet CrowdTangle Posts By Id CLI Action
# =============================================================================
#
# Logic of the `ct posts-by-id` action.
#
from ural import ensure_protocol
from ural.facebook import is_facebook_post_url

import minet.facebook as facebook
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.crowdtangle.utils import with_crowdtangle_utilities
from minet.crowdtangle.constants import CROWDTANGLE_POST_CSV_HEADERS
from minet.crowdtangle.exceptions import (
    CrowdTanglePostNotFound,
)


@with_crowdtangle_utilities
@with_enricher_and_loading_bar(
    headers=CROWDTANGLE_POST_CSV_HEADERS, title="Retrieving posts", unit="posts"
)
def action(cli_args, client, enricher, loading_bar):
    for row, url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
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

                if post is not None:
                    enricher.writerow(row, post.as_csv_row())
                else:
                    enricher.writerow(row)
            except CrowdTanglePostNotFound as error:
                enricher.writerow(row)
                loading_bar.print(
                    "\n\n"
                    "CrowdTangle does not have data about the post at this url: {url}\n"
                    "The CrowdTangle API's response is: \n{data}\n".format(
                        url=url, data=error.data
                    )
                )
