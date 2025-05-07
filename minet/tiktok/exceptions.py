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


class TiktokAuthenticationError(TiktokError):
    pass


class TiktokHTTPAPIError(TiktokError):
    def __init__(self, error):
        super().__init__()
        self.code = error["code"]
        self.message = error["message"]
        self.log_id = error["log_id"]

    def __str__(self):
        return "Error: %s, message: %s, log_id: %s" % (
            self.code,
            self.message,
            self.log_id,
        )
