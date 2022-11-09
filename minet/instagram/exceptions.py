# =============================================================================
# Minet Instagram Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class InstagramError(MinetError):
    pass


class InstagramPublicAPIInvalidResponseError(InstagramError):
    def __init__(self, url, status, data):
        super().__init__()
        self.url = url
        self.status = status
        self.data = data

    def __str__(self):
        return super().__str__() + ", Url: %s, Status: %i, Data: %s" % (
            self.url,
            self.status,
            self.data,
        )


class InstagramInvalidCookieError(InstagramError):
    pass


class InstagramTooManyRequestsError(InstagramError):
    pass


class InstagramError500(InstagramError):
    pass


class InstagramInvalidTargetError(InstagramError):
    pass


class InstagramNoPublicationError(InstagramError):
    pass


class InstagramPrivateOrNonExistentAccountError(InstagramError):
    pass


class InstagramHashtagNeverUsedError(InstagramError):
    pass


class InstagramPrivateAccountError(InstagramError):
    pass


class InstagramAccountNoFollowError(InstagramError):
    pass
