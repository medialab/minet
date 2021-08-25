# =============================================================================
# Minet Twitter Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class TwitterError(MinetError):
    pass


class TwitterGuestTokenError(TwitterError):
    pass


class TwitterPublicAPIQueryTooLongError(TwitterError):
    pass


class TwitterPublicAPIRateLimitError(TwitterError):
    pass


class TwitterPublicAPIInvalidResponseError(TwitterError):
    pass


class TwitterPublicAPIBadRequest(TwitterError):
    pass


class TwitterPublicAPIOverCapacityError(TwitterError):
    pass


class TwitterPublicAPIParsingError(TwitterError):
    pass


class TwitterPublicAPIHiccupError(TwitterError):
    pass
