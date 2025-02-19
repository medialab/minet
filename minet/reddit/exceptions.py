# =============================================================================
# Minet Reddit Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class RedditError(MinetError):
    pass


class RedditInvalidTargetError(RedditError):
    pass
