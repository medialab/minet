# =============================================================================
# Minet Custom CLI Exceptions
# =============================================================================
#
# Collection of handy custom exceptions.
#
from minet.exceptions import MinetError


class MinetCLIError(MinetError):
    pass


class InvalidArgumentsError(MinetCLIError):
    pass


class MissingColumnError(MinetCLIError):
    def __init__(self, message, column):
        super().__init__(message)
        self.column = column


class NotResumable(MinetCLIError):
    pass
