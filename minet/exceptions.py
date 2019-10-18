# =============================================================================
# Minet Custom Exceptions
# =============================================================================
#
# Collection of handy custom exceptions.
#


# General errors
class UnknownEncodingError(Exception):
    pass


# Miscellaneous HTTP errors
class InvalidURLError(Exception):
    pass


# Redirection errors
class RedirectError(Exception):
    pass


class MaxRedirectsError(RedirectError):
    pass


class InfiniteRedirectsError(RedirectError):
    pass


class SelfRedirectError(InfiniteRedirectsError):
    pass


class InvalidRedirectError(RedirectError):
    pass
