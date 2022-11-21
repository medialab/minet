# =============================================================================
# Minet Telegram Channel-Infos CLI Action
# =============================================================================
#
# Action retrieving the information of a Telegram channel.
#
import casanova

from minet.cli.utils import LoadingBar
from minet.telegram import TelegramScraper
from minet.telegram.constants import TELEGRAM_INFOS_CSV_HEADERS
from minet.telegram.exceptions import TelegramInvalidTargetError


def channel_infos_action(cli_args):
    scraper = TelegramScraper(throttle=cli_args.throttle)
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=TELEGRAM_INFOS_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar("Retrieving infos", unit="channel")

    for i, (row, channel) in enumerate(
        enricher.cells(cli_args.column, with_rows=True), 1
    ):
        loading_bar.inc("channels")

        try:
            infos = scraper.channel_infos(channel)

            enricher.writerow(row, infos)

            loading_bar.update()

        except TelegramInvalidTargetError:
            loading_bar.print(
                "%s (line %i) is not a telegram channel or url, or is not accessible."
                % (channel, i)
            )
