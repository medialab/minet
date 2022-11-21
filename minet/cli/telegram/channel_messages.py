# =============================================================================
# Minet Telegram Channel-Messages CLI Action
# =============================================================================
#
# Action retrieving the information of a Telegram channel.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.telegram import TelegramScraper
from minet.telegram.constants import TELEGRAM_MESSAGES_CSV_HEADERS
from minet.telegram.exceptions import TelegramInvalidTargetError


def channel_messages_action(cli_args):
    scraper = TelegramScraper(throttle=cli_args.throttle)
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=TELEGRAM_MESSAGES_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar("Retrieving messages", unit="message")

    for i, (row, channel) in enumerate(
        enricher.cells(cli_args.column, with_rows=True), 1
    ):
        loading_bar.inc("channels")

        try:
            messages = scraper.channel_messages(channel)

            for message in messages:
                enricher.writerow(row, message)
                loading_bar.update()

        except TelegramInvalidTargetError:
            loading_bar.print(
                "%s (line %i) is not a telegram channel or url, or is not accessible."
                % (channel, i)
            )
