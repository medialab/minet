# =============================================================================
# Minet Instagram User-infos CLI Action
# =============================================================================
#
# Logic of the `instagram user-infos` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.instagram.utils import with_instagram_fatal_errors
from minet.instagram import InstagramAPIScraper
from minet.instagram.constants import INSTAGRAM_USER_INFO_CSV_HEADERS
from minet.instagram.exceptions import InstagramInvalidTargetError


@with_instagram_fatal_errors
@with_enricher_and_loading_bar(
    headers=INSTAGRAM_USER_INFO_CSV_HEADERS, title="Scraping infos", unit="users"
)
def action(cli_args, enricher, loading_bar):
    client = InstagramAPIScraper(cookie=cli_args.cookie)

    for i, row, user in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step():
            try:
                result = client.user_infos(user)

                enricher.writerow(row, result.as_csv_row())

            except InstagramInvalidTargetError:
                loading_bar.print(
                    "Given user (line %i) is probably not an Instagram user: %s"
                    % (i, user)
                )
