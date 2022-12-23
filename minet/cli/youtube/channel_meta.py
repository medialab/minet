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
from minet.youtube.constants import YOUTUBE_CHANNEL_CSV_HEADERS
from minet.youtube.exceptions import YouTubeInvalidChannelTargetError


def channel_meta_action(cli_args):
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=YOUTUBE_CHANNEL_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar(
        desc="Retrieving meta", unit="channel", total=cli_args.total
    )

    def before_sleep_until_midnight(seconds):
        loading_bar.print(
            "API limits reached. Will now wait until midnight Pacific time!"
        )

    client = YouTubeAPIClient(
        cli_args.key, before_sleep_until_midnight=before_sleep_until_midnight
    )

    for row, channel_id in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        try:
            result = client.channel_meta(channel_id)

            enricher.writerow(row, result.as_csv_row() if result else None)
        except YouTubeInvalidChannelTargetError:
            loading_bar.print(
                "\nWe did not manage to reach this channel: %s" % channel_id
            )
