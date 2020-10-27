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
    def __init__(self, message=None, status=None, code=None):
        super().__init__(message)
        self.code = code
        self.status = status

    def __str__(self):
        return super().__str__() + ', Code: %i, Status: %i' % (self.code, self.status)


class CrowdTangleMissingStartDateError(CrowdTangleError):
    pass


class CrowdTangleInvalidJSONError(CrowdTangleError):
    pass


class CrowdTangleRateLimitExceeded(CrowdTangleError):
    pass
