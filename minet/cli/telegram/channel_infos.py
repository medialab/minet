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


def channel_infos_action(cli_args):
    scraper = TelegramScraper(throttle=cli_args.throttle)
    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=TELEGRAM_INFOS_CSV_HEADERS,
        keep=cli_args.select,
    )

    loading_bar = LoadingBar("Retrieving infos", unit="channel")

    for row, channel in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.update()

        infos = scraper.channel_infos(channel)

        enricher.writerow(row, infos)
