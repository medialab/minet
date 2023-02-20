# =============================================================================
# Minet Facebook Comments CLI Action
# =============================================================================
#
# Logic of the `fb comments` action.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.facebook.utils import with_facebook_fatal_errors
from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import FACEBOOK_COMMENT_CSV_HEADERS
from minet.facebook.exceptions import FacebookInvalidTargetError


@with_facebook_fatal_errors
@with_enricher_and_loading_bar(
    headers=FACEBOOK_COMMENT_CSV_HEADERS,
    title="Scraping comments",
    unit="posts",
    nested=True,
    sub_unit="comments",
    stats=[
        {"name": "calls", "style": "info"},
        {"name": "q", "style": "info"},
        {"name": "replies", "style": "info"},
        {"name": "invalid targets", "style": "error"},
    ],
)
def action(cli_args, enricher, loading_bar):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    for row, url in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.nested_task(url):
            try:
                batches = scraper.comments(url, per_call=True, detailed=True)
            except FacebookInvalidTargetError:
                loading_bar.inc_stat("invalid targets")
                continue

            for _, batch in batches:
                for comment in batch:
                    enricher.writerow(row, comment.as_csv_row())
                    loading_bar.nested_advance()

                # loading_bar.update(
                #     calls=details["calls"],
                #     replies=details["replies"],
                #     q=details["queue_size"],
                # )
