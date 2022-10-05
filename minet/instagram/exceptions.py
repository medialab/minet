# =============================================================================
# Minet Instagram Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class InstagramError(MinetError):
    pass


class InstagramPublicAPIInvalidResponseError(InstagramError):
    pass


class InstagramInvalidCookieError(InstagramError):
    pass


class InstagramTooManyRequestsError(InstagramError):
    pass


class InstagramError500(InstagramError):
    pass
