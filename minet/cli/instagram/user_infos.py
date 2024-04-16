# =============================================================================
# Minet Instagram User-infos CLI Action
# =============================================================================
#
# Logic of the `instagram user-infos` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.types import InstagramUserInfo
from minet.instagram.exceptions import InstagramInvalidTargetError


@with_instagram_fatal_errors
@with_enricher_and_loading_bar(
    headers=InstagramUserInfo, title="Scraping infos", unit="users"
)
def action(cli_args, enricher, loading_bar: LoadingBar):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    for row, user in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            try:
                info = client.user_infos(user)
                enricher.writerow(row, info)

            except InstagramInvalidTargetError:
                loading_bar.inc_stat("not-found", style="warning")
                enricher.writerow(row)
