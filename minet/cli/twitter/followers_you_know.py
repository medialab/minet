# =============================================================================
# Minet Twitter Scrape CLI Action
# =============================================================================
#
# Logic of the `tw scrape` action.
#
from twitwi.constants import USER_FIELDS
from twitwi import format_user_as_csv_row

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.exceptions import FatalError
from minet.twitter import TwitterAPIScraper
from minet.twitter.exceptions import (
    TwitterPublicAPIInvalidCookieError,
    TwitterPublicAPIBadAuthError,
)


@with_enricher_and_loading_bar(
    headers=USER_FIELDS,
    title="Scraping",
    unit="users",
    nested=True,
    sub_unit="followers",
)
def action(cli_args, enricher, loading_bar):
    try:
        scraper = TwitterAPIScraper(cli_args.cookie)
    except TwitterPublicAPIInvalidCookieError:
        raise FatalError(
            [
                "Invalid Twitter cookie!",
                "Try giving another browser to --cookie and sure you are correctly logged in.",
            ]
        )

    for row, user_id in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(user_id):
            iterator = scraper.followers_you_know(user_id, locale=cli_args.timezone)

            try:
                for user in iterator:
                    addendum = format_user_as_csv_row(user)
                    enricher.writerow(row, addendum)
                    loading_bar.nested_advance()

            except TwitterPublicAPIBadAuthError as error:
                raise FatalError(
                    "Bad authentication (%i). Double check your --cookie and make sure you are logged in."
                    % error.status
                )
