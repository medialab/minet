# =============================================================================
# Minet Custom Exceptions
# =============================================================================
#
# Collection of handy custom exceptions.
#


class MinetError(Exception):
    pass


# General errors
class UnknownEncodingError(MinetError):
    pass


# Miscellaneous HTTP errors
class InvalidURLError(MinetError):
    pass


# Redirection errors
class RedirectError(MinetError):
    pass


class MaxRedirectsError(RedirectError):
    pass


class InfiniteRedirectsError(RedirectError):
    pass


class SelfRedirectError(InfiniteRedirectsError):
    pass


class InvalidRedirectError(RedirectError):
    pass


# Crawling errors
class CrawlError(MinetError):
    pass


class UnknownSpiderError(CrawlError):
    pass
