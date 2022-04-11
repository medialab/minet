# =============================================================================
# Minet Youtube Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube videos using Google's APIs.
#
import casanova
from operator import itemgetter

from minet.cli.utils import LoadingBar
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_VIDEO_CSV_HEADERS


def videos_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=YOUTUBE_VIDEO_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar("Retrieving videos", unit="video", total=cli_args.total)

    def before_sleep_until_midnight(seconds):
        loading_bar.print(
            "API limits reached. Will now wait until midnight Pacific time!"
        )

    client = YouTubeAPIClient(
        cli_args.key, before_sleep_until_midnight=before_sleep_until_midnight
    )

    iterator = enricher.cells(cli_args.column, with_rows=True)

    for (row, _), video in client.videos(iterator, key=itemgetter(1)):
        loading_bar.update()
        enricher.writerow(row, video.as_csv_row() if video else None)
