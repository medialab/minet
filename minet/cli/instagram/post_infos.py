# =============================================================================
# Minet Instagram Post-infos CLI Action
# =============================================================================
#
# Logic of the `instagram post-infos` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.types import InstagramPost
from minet.instagram.exceptions import InstagramInvalidTargetError


@with_instagram_fatal_errors
@with_enricher_and_loading_bar(
    headers=InstagramPost, title="Scraping infos", unit="posts"
)
def action(cli_args, enricher, loading_bar):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    for i, row, user in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step():
            try:
                result = client.post_infos(user)

                enricher.writerow(row, result)

            except InstagramInvalidTargetError:
                loading_bar.print(
                    "Given post (line %i) is probably not an Instagram post: %s"
                    % (i, user)
                )
