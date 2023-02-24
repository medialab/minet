# =============================================================================
# Minet Instagram Post-infos CLI Action
# =============================================================================
#
# Logic of the `instagram post-infos` action.
#

import casanova

from minet.cli.utils import LoadingBar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_POST_CSV_HEADERS
from minet.instagram.exceptions import InstagramInvalidTargetError


@with_instagram_fatal_errors
def action(cli_args):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    enricher = casanova.enricher(
        cli_args.input,
        cli_args.output,
        add=INSTAGRAM_POST_CSV_HEADERS,
    )

    loading_bar = LoadingBar("Retrieving infos", unit="post")

    for i, (row, post) in enumerate(enricher.cells(cli_args.column, with_rows=True)):
        loading_bar.update()

        try:
            result = client.post_infos(post)

            enricher.writerow(row, result.as_csv_row())

        except InstagramInvalidTargetError:
            loading_bar.print(
                "Given post (line %i) is probably not an Instagram post: %s" % (i, post)
            )
