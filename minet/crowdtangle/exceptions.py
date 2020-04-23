# =============================================================================
# Minet CrowdTangle Exceptions.
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
    pass


class CrowdTangleMissingStartDateError(CrowdTangleError):
    pass


class CrowdTangleInvalidJSONError(CrowdTangleError):
    pass


class CrowdTangleExhaustedPagination(CrowdTangleError):
    pass
