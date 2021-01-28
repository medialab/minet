# =============================================================================
# Minet Twitter Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class TwitterError(MinetError):
    pass


class TwitterGuestTokenError(TwitterError):
    pass
