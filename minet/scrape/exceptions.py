# =============================================================================
# Minet Scrape Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class ScrapeError(MinetError):
    pass


class CSSSelectorTooComplex(ScrapeError):
    pass


class ScraperRuntimeError(ScrapeError):
    def __init__(self, msg=None, reason=None, expression=None, path=None):
        super().__init__(msg)
        self.reason = reason
        self.expression = expression
        self.path = path


class ScraperEvalError(ScraperRuntimeError):
    pass


class NotATableError(ScraperRuntimeError):
    pass


class ScraperEvalSyntaxError(ScraperRuntimeError):
    pass


class ScraperEvalTypeError(ScraperRuntimeError):
    def __init__(self, msg=None, expected=None, got=None, **kwargs):
        super().__init__(msg, **kwargs)
        self.expected = expected
        self.got = got


class ScraperEvalNoneError(ScraperRuntimeError):
    pass


class ScraperValidationError(ScraperRuntimeError):
    pass


class ScraperValidationConflictError(ScraperRuntimeError):
    def __init__(self, msg=None, keys=[], **kwargs):
        super().__init__(msg, **kwargs)
        self.keys = keys


class InvalidCSSSelectorError(ScraperRuntimeError):
    pass
