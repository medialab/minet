# =============================================================================
# Minet YouTube Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class YouTubeError(MinetError):
    pass


class YouTubeInvalidAPIKeyError(YouTubeError):
    pass
