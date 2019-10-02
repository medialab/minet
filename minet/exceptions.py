# =============================================================================
# Minet Custom Exceptions
# =============================================================================
#
# Collection of handy custom exceptions.
#


# Miscellaneous HTTP errors
class InvalidURLError(Exception):
    pass


# Redirection errors
class MaxRedirectsError(Exception):
    pass


class InfiniteRedirectsError(Exception):
    pass


class SelfRedirectError(InfiniteRedirectsError):
    pass


class InvalidRedirectError(Exception):
    pass
