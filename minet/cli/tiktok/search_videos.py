# =============================================================================
# Minet Tiktok Search-videos CLI Action
# =============================================================================
#
# Logic of the `tiktok search-videos` action.
#
import casanova
from itertools import islice

from minet.cli.utils import LoadingBar
from minet.tiktok import TiktokAPIScraper
from minet.tiktok.constants import TIKTOK_VIDEO_CSV_HEADERS


def search_videos_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=TIKTOK_VIDEO_CSV_HEADERS,
    )

    loading_bar = LoadingBar("Retrieving videos", unit="querie", stats={"videos": 0})

    client = TiktokAPIScraper(cookie=cli_args.cookie)
    for row, query in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        generator = client.search_videos(query)

        if cli_args.limit:
            generator = islice(generator, cli_args.limit)

        for video in generator:
            enricher.writerow(row, video.as_csv_row())

            loading_bar.inc("videos")
