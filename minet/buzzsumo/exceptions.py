# =============================================================================
# Minet BuzzSumo Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class BuzzSumoError(MinetError):
    pass


class BuzzSumoInvalidTokenError(BuzzSumoError):
    pass


class BuzzSumoInvalidQueryError(BuzzSumoError):
    def __init__(self, url=None, msg=None):
        super().__init__()
        self.url = url
        self.msg = msg


class BuzzSumoBadRequestError(BuzzSumoError):
    pass


class BuzzSumoOutageError(BuzzSumoError):
    pass
