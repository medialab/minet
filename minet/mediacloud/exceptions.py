# =============================================================================
# Minet Mediacloud Exceptions.
# =============================================================================
#
from minet.exceptions import MinetError


class MediacloudError(MinetError):
    pass


class MediacloudServerError(MediacloudError):
    pass


class MediacloudInvalidQueryError(MediacloudError):
    pass
