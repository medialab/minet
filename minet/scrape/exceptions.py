# =============================================================================
# Minet Scrape Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class ScrapeError(MinetError):
    pass


class BaseScrapeRuntimeError(ScrapeError):
    def __init__(self, msg=None, reason=None, expression=None, path=None):
        super().__init__(msg)
        self.reason = reason
        self.expression = expression
        self.path = path


class ScrapeEvalError(BaseScrapeRuntimeError):
    pass


class ScrapeEvalSyntaxError(BaseScrapeRuntimeError):
    pass


class ScrapeEvalTypeError(BaseScrapeRuntimeError):
    def __init__(self, msg=None, expected=None, got=None, **kwargs):
        super().__init__(msg, **kwargs)
        self.expected = expected
        self.got = got


class ScrapeEvalNoneError(BaseScrapeRuntimeError):
    pass


class ScrapeValidationError(BaseScrapeRuntimeError):
    pass


class ScrapeValidationConflictError(BaseScrapeRuntimeError):
    def __init__(self, msg=None, keys=[], **kwargs):
        super().__init__(msg, **kwargs)
        self.keys = keys
