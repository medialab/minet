# =============================================================================
# Minet Tiktok Search-videos CLI Action
# =============================================================================
#
# Logic of the `tiktok search-videos` action.
#
from itertools import islice

from minet.cli.utils import with_enricher_and_loading_bar
from minet.tiktok import TiktokAPIScraper
from minet.tiktok.constants import TIKTOK_VIDEO_CSV_HEADERS


@with_enricher_and_loading_bar(
    headers=TIKTOK_VIDEO_CSV_HEADERS,
    title="Searching videos",
    unit="queries",
    nested=True,
    sub_unit="videos",
)
def action(cli_args, enricher, loading_bar):
    client = TiktokAPIScraper(cookie=cli_args.cookie)

    for row, query in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(query):
            generator = client.search_videos(query)

            if cli_args.limit:
                generator = islice(generator, cli_args.limit)

            for video in generator:
                enricher.writerow(row, video.as_csv_row())
                loading_bar.nested_advance()
