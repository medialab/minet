# =============================================================================
# Minet Telegram Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class TelegramError(MinetError):
    pass


class TelegramInvalidTargetError(TelegramError):
    pass
