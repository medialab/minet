# =============================================================================
# Minet Youtube Channel CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube channels using Google's APIs.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_PLAYLIST_VIDEO_SNIPPET_CSV_HEADERS


def channel_videos_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=YOUTUBE_PLAYLIST_VIDEO_SNIPPET_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar(desc="Retrieving videos", unit="video")

    def before_sleep_until_midnight(seconds):
        loading_bar.print(
            "API limits reached. Will now wait until midnight Pacific time!"
        )

    client = YouTubeAPIClient(
        cli_args.key, before_sleep_until_midnight=before_sleep_until_midnight
    )

    for row, channel_id in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.print('Retrieving videos for "%s"' % channel_id)
        for video in client.channel_videos(channel_id):
            loading_bar.update()
            enricher.writerow(row, video.as_csv_row())

        loading_bar.inc("channels")
