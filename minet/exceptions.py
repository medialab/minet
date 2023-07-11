# =============================================================================
# Minet Custom Exceptions
# =============================================================================
#
# Collection of handy custom exceptions.
#
from typing import Optional

from minet.utils import message_flatmap


# Base minet error
class MinetError(Exception):
    def __init__(self, message=None):
        if message:
            message = message_flatmap(message)

        self.message = message or ""

        if not message:
            super().__init__()
        else:
            super().__init__(message)

    def __repr__(self):
        representation = "<" + self.__class__.__name__

        for k in dir(self):
            if k.startswith("_") or k == "args" or "traceback" in k:
                continue

            v = getattr(self, k)

            if v is None:
                continue

            if isinstance(v, BaseException):
                representation += " {k}=<{name}>".format(k=k, name=v.__class__.__name__)
                continue

            if isinstance(v, str) and len(v) > 30:
                v = v[:29] + "…"

            representation += " {k}={v!r}".format(k=k, v=v)

        representation += ">"

        return representation


# General errors
class UnknownEncodingError(MinetError):
    pass


class CouldNotInferEncodingError(MinetError):
    pass


# Cookie errors
class UnknownBrowserError(MinetError):
    def __init__(self, browser: str):
        super().__init__("Unknown browser: %s" % browser)
        self.browser = browser


class CookieGrabbingError(MinetError):
    def __init__(self, browser: str, reason: Exception):
        super().__init__("Could not grab cookies from: %s" % browser)
        self.browser = browser
        self.reason = reason


# Miscellaneous HTTP errors
class InvalidURLError(MinetError):
    def __init__(self, url: str):
        self.url = url
        super().__init__(url)


class InvalidStatusError(MinetError):
    def __init__(self, status: int):
        super().__init__(str(status))
        self.status = status


class HTTPCallbackError(MinetError):
    def __init__(self, reason: Exception):
        super().__init__("HTTPCallbackError: " + str(reason))
        self.reason = reason

    def unwrap(self, allow) -> Exception:
        if not isinstance(self.reason, allow):
            raise self.reason

        return self.reason


class CancelledRequestError(MinetError):
    pass


class FinalTimeoutError(MinetError):
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


class BadlyEncodedLocationHeaderError(RedirectError):
    pass


# Definition errors
class DefinitionInvalidFormatError(MinetError):
    pass


# Crawling errors
class CrawlError(MinetError):
    pass


class UnknownSpiderError(CrawlError):
    def __init__(self, spider: str):
        super().__init__(spider)
        self.spider = spider


# Extraction errors
class TrafilaturaError(MinetError):
    def __init__(self, message=None, reason=None):
        super().__init__(message)
        self.reason = reason


# Filesystem errors
class FilenameFormattingError(MinetError):
    def __init__(self, message=None, reason=None, template=None):
        super().__init__(message)
        self.reason = reason
        self.template = template


# User Agents error
class UserAgentsUpdateError(MinetError):
    def __init__(self, message=None, reason: Optional[BaseException] = None):
        super().__init__(message)
        self.reason = reason
