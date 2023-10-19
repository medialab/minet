# =============================================================================
# Minet Youtube Channel Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving videos from
# the given Youtube channels using Google's APIs.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.youtube import YouTubeAPIClient
from minet.youtube.types import YouTubePlaylistVideoSnippet


@with_enricher_and_loading_bar(
    headers=YouTubePlaylistVideoSnippet,
    title="Retrieving channel videos",
    unit="channels",
    sub_unit="videos",
    nested=True,
)
def action(cli_args, enricher, loading_bar):
    client = YouTubeAPIClient(cli_args.key)

    for row, channel_id in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(channel_id):
            for video in client.channel_videos(channel_id):
                enricher.writerow(row, video)
                loading_bar.nested_advance()
