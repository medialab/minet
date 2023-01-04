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
from minet.youtube.constants import YOUTUBE_CHANNEL_TOPIC_ID_CSV_HEADERS


def channel_topic_ids(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=YOUTUBE_CHANNEL_TOPIC_ID_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar(desc="Retrieving channel topics", unit="channel")

    def before_sleep_until_midnight(seconds):
        loading_bar.print(
            "API limits reached. Will now wait until midnight Pacific time!"
        )

    client = YouTubeAPIClient(
        cli_args.key, before_sleep_until_midnight=before_sleep_until_midnight
    )
    
    for row, channel_target in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.print('Searching for "%s"' % channel_target)

        iterator = client.channel_topics(channel_target)

        for item in iterator:
            loading_bar.update()
            enricher.writerow(row, item.as_csv_row())
    