# =============================================================================
# Minet Scrape Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class ScrapeError(MinetError):
    pass


class ScrapeEvalError(ScrapeError):
    def __init__(self, msg, reason=None, expression=None):
        super().__init__(msg)
        self.reason = reason
        self.expression = expression


class ScrapeEvalSyntaxError(ScrapeError):
    pass


class ScrapeEvalTypeError(ScrapeError):
    pass
