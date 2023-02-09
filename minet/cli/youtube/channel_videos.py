# =============================================================================
# Minet Youtube Channel Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving videos from
# the given Youtube channels using Google's APIs.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_PLAYLIST_VIDEO_SNIPPET_CSV_HEADERS


def action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=YOUTUBE_PLAYLIST_VIDEO_SNIPPET_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar(desc="Retrieving videos", unit="video")

    client = YouTubeAPIClient(cli_args.key)

    for row, channel_id in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.print('Retrieving videos for "%s"' % channel_id)
        for video in client.channel_videos(channel_id):
            loading_bar.update()
            enricher.writerow(row, video.as_csv_row())

        loading_bar.inc("channels")
