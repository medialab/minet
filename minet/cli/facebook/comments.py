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
    ],
)
def action(cli_args, enricher, loading_bar):
    scraper = FacebookMobileScraper(cli_args.cookie, throttle=cli_args.throttle)

    for i, row, url in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step(url):
            try:
                batches = scraper.comments(url, per_call=True, detailed=True)
            except FacebookInvalidTargetError:
                loading_bar.print(
                    "Given url (line %i) is probably not a Facebook group post: %s"
                    % (i, url)
                )
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
