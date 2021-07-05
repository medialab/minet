# =============================================================================
# Minet CrowdTangle Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class CrowdTangleError(MinetError):
    pass


class CrowdTangleMissingTokenError(CrowdTangleError):
    pass


class CrowdTangleInvalidTokenError(CrowdTangleError):
    pass


class CrowdTangleInvalidRequestError(CrowdTangleError):
    def __init__(self, message=None, url=None, status=None, code=None):
        super().__init__(message)
        self.url = url
        self.code = code
        self.status = status

    def __str__(self):
        if self.status is None:
            return super().__str__()

        return super().__str__() + ', Url: %s, Code: %s, Status: %s' % (self.url, self.code, self.status)


class CrowdTangleServerError(CrowdTangleError):
    def __init__(self, url=None, status=None):
        super().__init__()
        self.url = url
        self.status = status

    def __str__(self):
        if self.status is None:
            return super().__str__()

        return super().__str__() + '%s Status: %s' % (self.url, self.status)


class CrowdTangleMissingStartDateError(CrowdTangleError):
    pass


class CrowdTangleInvalidJSONError(CrowdTangleError):
    pass


class CrowdTangleRateLimitExceeded(CrowdTangleError):
    pass
