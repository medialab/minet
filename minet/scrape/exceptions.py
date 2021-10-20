# =============================================================================
# Minet Scrape Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class ScrapeError(MinetError):
    pass


class InvalidScraperError(ScrapeError):
    def __init__(self, msg=None, validation_errors=[]):
        super().__init__(msg)
        self.validation_errors = validation_errors


class CSSSelectorTooComplex(ScrapeError):
    pass


class ScraperNotTabularError(ScrapeError):
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


class ScraperValidationMixedConcernError(ScraperRuntimeError):
    pass


class ScraperValidationUnknownKeyError(ScraperRuntimeError):
    def __init__(self, msg=None, key=None, **kwargs):
        super().__init__(msg, **kwargs)
        self.key = key


class ScraperValidationConflictError(ScraperRuntimeError):
    def __init__(self, msg=None, keys=[], **kwargs):
        super().__init__(msg, **kwargs)
        self.keys = keys


class ScraperValidationIrrelevantPluralModifierError(ScraperRuntimeError):
    def __init__(self, msg=None, modifier=None, **kwargs):
        super().__init__(msg, **kwargs)
        self.modifier = modifier


class ScraperValidationInvalidPluralModifierError(ScraperRuntimeError):
    def __init__(self, msg=None, modifier=None, **kwargs):
        super().__init__(msg, **kwargs)
        self.modifier = modifier


class ScraperValidationInvalidExtractorError(ScraperRuntimeError):
    def __init__(self, msg=None, extractor=None, **kwargs):
        super().__init__(msg, **kwargs)
        self.extractor = extractor


class InvalidCSSSelectorError(ScraperRuntimeError):
    pass
