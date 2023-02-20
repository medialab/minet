# =============================================================================
# Minet Youtube Channel CLI Action
# =============================================================================
#
# Action reading an input CSV file line by line and retrieving metadata about
# the given Youtube channels using Google's APIs.
#
from operator import itemgetter

from minet.cli.utils import with_enricher_and_loading_bar
from minet.youtube import YouTubeAPIClient
from minet.youtube.constants import YOUTUBE_CHANNEL_CSV_HEADERS


@with_enricher_and_loading_bar(
    headers=YOUTUBE_CHANNEL_CSV_HEADERS,
    title="Retrieving channel data",
    unit="channels",
)
def action(cli_args, enricher, loading_bar):
    client = YouTubeAPIClient(cli_args.key)

    iterator = enricher.cells(cli_args.column, with_rows=True)

    for (row, _), channel in client.channels(iterator, key=itemgetter(1)):
        enricher.writerow(row, channel.as_csv_row() if channel else None)
        loading_bar.advance()
