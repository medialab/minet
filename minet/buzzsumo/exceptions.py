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
    def __init__(self, msg=None, url=None, data=None):
        super().__init__(msg)
        self.url = url
        self.data = data


class BuzzSumoBadRequestError(BuzzSumoError):
    pass


class BuzzSumoOutageError(BuzzSumoError):
    pass


class BuzzSumoRateLimitedError(BuzzSumoError):
    pass
