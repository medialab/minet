# =============================================================================
# Minet Facebook Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class FacebookError(MinetError):
    pass


class FacebookInvalidTargetError(FacebookError):
    pass
