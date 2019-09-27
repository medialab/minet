# =============================================================================
# Minet Custom Exceptions
# =============================================================================
#
# Collection of handy custom exceptions.
#


class MaxRedirectsError(Exception):
    pass


class InfiniteRedirectsError(Exception):
    pass


class InvalidRedirectError(Exception):
    pass
