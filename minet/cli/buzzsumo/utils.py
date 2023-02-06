from minet.cli.utils import with_fatal_errors
from minet.buzzsumo.exceptions import (
    BuzzSumoInvalidTokenError,
    BuzzSumoInvalidQueryError,
)

FATAL_ERRORS = {BuzzSumoInvalidTokenError: "Your BuzzSumo token is invalid!"}


def fatal_errors_hook(_, e):
    if isinstance(e, BuzzSumoInvalidQueryError):
        return ["Invalid query: %s" % e.url, "Message from the API: %s" % e]

    return FATAL_ERRORS.get(type(e))


def with_buzzsumo_fatal_errors(fn):
    return with_fatal_errors(fatal_errors_hook)(fn)
