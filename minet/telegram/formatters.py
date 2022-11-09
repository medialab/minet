# =============================================================================
# Minet Telegram Formatters
# =============================================================================
#
# Various formatters for Telegram data.
#
from casanova import namedrecord

from minet.telegram.constants import (
    TELEGRAM_INFOS_CSV_HEADERS,
    TELEGRAM_MESSAGES_CSV_HEADERS,
)

TelegramChannelInfos = namedrecord("TelegramChannelInfos", TELEGRAM_INFOS_CSV_HEADERS)
TelegramChannelMessages = namedrecord(
    "TelegramChannelMessages", TELEGRAM_MESSAGES_CSV_HEADERS
)
