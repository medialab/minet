# =============================================================================
# Minet Scrape Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class ScrapeError(MinetError):
    pass


class ScrapeEvalError(ScrapeError):
    def __init__(self, msg=None, reason=None, expression=None):
        super().__init__(msg)
        self.reason = reason
        self.expression = expression


class ScrapeEvalSyntaxError(ScrapeError):
    def __init__(self, msg=None, reason=None, expression=None, path=None):
        super().__init__(msg)
        self.reason = reason
        self.expression = expression
        self.path = path


class ScrapeEvalTypeError(ScrapeError):
    pass
