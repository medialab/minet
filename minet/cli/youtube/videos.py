# =============================================================================
# Minet Youtube Videos CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube videos using Google's APIs.
#
from operator import itemgetter

from minet.cli.utils import with_enricher_and_loading_bar
from minet.youtube import YouTubeAPIClient
from minet.youtube.types import YouTubeVideo


@with_enricher_and_loading_bar(
    headers=YouTubeVideo, title="Retrieving videos", unit="videos"
)
def action(cli_args, enricher, loading_bar):
    client = YouTubeAPIClient(cli_args.key)

    iterator = enricher.cells(cli_args.column, with_rows=True)

    for (row, _), video in client.videos(iterator, key=itemgetter(1)):
        with loading_bar.step():
            enricher.writerow(row, video)
