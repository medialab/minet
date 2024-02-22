# =============================================================================
# Minet Facebook User Places Lived CLI Action
# =============================================================================
#
# Logic of the `fb user-places-lived` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.facebook.utils import with_facebook_fatal_errors
from minet.facebook import FacebookMobileScraper
from minet.facebook.types import MobileFacebookUserInfo

@with_facebook_fatal_errors
@with_enricher_and_loading_bar(
    headers=MobileFacebookUserInfo, title="Finding user profile infos", unit="users"
)
def action(cli_args, enricher, loading_bar):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    for i, row, user_url in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step():
            user_infos = scraper.user_infos(user_url)
            print(row)
            enricher.writerow(row, user_infos.as_csv_row() if user_infos is not None else None)
