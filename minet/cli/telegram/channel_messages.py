# =============================================================================
# Minet Telegram Channel-Messages CLI Action
# =============================================================================
#
# Action retrieving the information of a Telegram channel.
#
from minet.cli.utils import with_enricher_and_loading_bar
from minet.telegram import TelegramScraper
from minet.telegram.constants import TELEGRAM_MESSAGES_CSV_HEADERS
from minet.telegram.exceptions import TelegramInvalidTargetError


@with_enricher_and_loading_bar(
    headers=TELEGRAM_MESSAGES_CSV_HEADERS,
    title="Collecting channel messages",
    unit="channels",
    nested=True,
    sub_unit="messages",
)
def action(cli_args, enricher, loading_bar):
    scraper = TelegramScraper(throttle=cli_args.throttle)

    for i, row, channel in enricher.enumerate_cells(
        cli_args.column, with_rows=True, start=1
    ):
        with loading_bar.step(channel):
            try:
                messages = scraper.channel_messages(channel)

                for message in messages:
                    enricher.writerow(row, message)
                    loading_bar.nested_advance()

            except TelegramInvalidTargetError:
                loading_bar.print(
                    "%s (line %i) is not a telegram channel or url, or is not accessible."
                    % (channel, i)
                )
