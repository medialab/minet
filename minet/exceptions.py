# =============================================================================
# Minet Custom Exceptions
# =============================================================================
#
# Collection of handy custom exceptions.
#


# Base minet error
class MinetError(Exception):
    def __init__(self, message=None):
        super().__init__('' if message is None else message)
        self.message = message

    def __repr__(self):
        representation = '<' + self.__class__.__name__

        for k in dir(self):
            if (
                k.startswith('_') or
                k == 'args' or
                'traceback' in k
            ):
                continue

            v = getattr(self, k)

            if v is None:
                continue

            if isinstance(v, BaseException):
                representation += ' {k}=<{name}>'.format(k=k, name=v.__class__.__name__)
                continue

            if isinstance(v, str) and len(v) > 30:
                v = v[:29] + '…'

            representation += ' {k}={v!r}'.format(k=k, v=v)

        representation += '>'

        return representation


# General errors
class UnknownEncodingError(MinetError):
    pass


# Miscellaneous HTTP errors
class InvalidURLError(MinetError):
    def __init__(self, message=None, url=None):
        self.url = url
        super().__init__(message)


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


# Definition errors
class DefinitionInvalidFormatError(MinetError):
    pass


# Crawling errors
class CrawlError(MinetError):
    pass


class UnknownSpiderError(CrawlError):
    pass


# Extraction errors
class TrafilaturaError(MinetError):
    def __init__(self, msg=None, reason=None):
        super().__init__(msg)
        self.reason = reason


# Filesystem errors
class FilenameFormattingError(MinetError):
    def __init__(self, msg=None, reason=None, template=None):
        super().__init__(msg)
        self.reason = reason
        self.template = template
