# =============================================================================
# Minet Facebook User Infos CLI Action
# =============================================================================
#
# Logic of the `fb user-infos` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.loading_bar import LoadingBar
from minet.cli.facebook.utils import with_facebook_fatal_errors
from minet.facebook import FacebookMobileScraper
from minet.facebook.types import MobileFacebookUserInfo


@with_facebook_fatal_errors
@with_enricher_and_loading_bar(
    headers=MobileFacebookUserInfo, title="Scraping user infos", unit="users"
)
def action(cli_args, enricher, loading_bar: LoadingBar):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    for row, user_url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step():
            try:
                user_infos = scraper.user_infos(user_url)
                enricher.writerow(row, user_infos)
            except TypeError:
                enricher.writerow(row)
                loading_bar.inc_stat("invalid-url", style="error")
