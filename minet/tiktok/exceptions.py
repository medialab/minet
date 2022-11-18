# =============================================================================
# Minet Tiktok Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class TiktokError(MinetError):
    pass


class TiktokPublicAPIInvalidResponseError(TiktokError):
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


class TiktokInvalidCookieError(TiktokError):
    pass
