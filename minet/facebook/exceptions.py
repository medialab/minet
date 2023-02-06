# =============================================================================
# Minet Facebook Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class FacebookError(MinetError):
    pass


class FacebookInvalidCookieError(FacebookError):
    def __init__(self, msg=None, target=None):
        super().__init__(msg)
        self.target = target


class FacebookInvalidTargetError(FacebookError):
    pass


class FacebookNotPostError(FacebookError):
    pass


class FacebookWatchError(FacebookError):
    pass
