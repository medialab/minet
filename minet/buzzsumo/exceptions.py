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
    pass


class BuzzSumoBadRequestError(BuzzSumoError):
    pass


class BuzzSumoOutageError(BuzzSumoError):
    pass
