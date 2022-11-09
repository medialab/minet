# =============================================================================
# Minet Facebook Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class FacebookError(MinetError):
    pass


class FacebookInvalidCookieError(FacebookError):
    pass


class FacebookInvalidTargetError(FacebookError):
    pass


class FacebookNotPostError(FacebookError):
    pass


class FacebookWatchError(FacebookError):
    pass
