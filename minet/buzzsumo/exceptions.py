# =============================================================================
# Minet BuzzSumo Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class BuzzSumoError(MinetError):
    pass


class BuzzSumoInvalidTokenError(BuzzSumoError):
    pass


class BuzzSumoInvalidRequestError(BuzzSumoError):
    pass


class BuzzSumoBadRequestError(BuzzSumoError):
    pass


class BuzzSumoOutageError(BuzzSumoError):
    pass
