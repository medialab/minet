# =============================================================================
# Minet Mediacloud Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class MediacloudError(MinetError):
    pass


class MediacloudServerError(MediacloudError):
    def __init__(self, message=None, server_error=None):
        super().__init__(message)
        self.server_error = server_error


class MediacloudInvalidQueryError(MediacloudError):
    pass
