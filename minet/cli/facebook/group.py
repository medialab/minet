# =============================================================================
# Minet Facebook Group CLI Action
# =============================================================================
#
# Logic of the `fb group` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.facebook.utils import with_facebook_fatal_errors
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_GROUP_OR_PAGE_CSV_HEADERS
from minet.facebook.exceptions import FacebookNotPostError
from minet.facebook.exceptions import FacebookCouldNotExtractError
from minet.facebook.exceptions import FacebookBlock


PADDING = [""] * len(FACEBOOK_GROUP_OR_PAGE_CSV_HEADERS)


@with_facebook_fatal_errors
@with_enricher_and_loading_bar(
    headers=["error"] + FACEBOOK_GROUP_OR_PAGE_CSV_HEADERS,
    title="Scraping groups",
    unit="group",
)
def action(cli_args, enricher, loading_bar):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(url):
            try:
                post = scraper.group_or_page(url)
                enricher.writerow(row, [""], post.as_csv_row())

            except FacebookCouldNotExtractError:
                enricher.writerow(row, ["could_not_extract"], PADDING)
            except FacebookBlock:
                break

            # TODO: something with url
