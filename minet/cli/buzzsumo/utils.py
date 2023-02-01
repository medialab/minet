from minet.cli.utils import with_fatal_errors
from minet.buzzsumo.exceptions import BuzzSumoInvalidTokenError

FATAL_ERRORS = {BuzzSumoInvalidTokenError: "Your BuzzSumo token is invalid!"}


def with_buzzsumo_fatal_errors(fn):
    return with_fatal_errors(FATAL_ERRORS)(fn)
