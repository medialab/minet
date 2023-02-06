from minet.cli.utils import with_fatal_errors
from minet.hyphe.exceptions import HypheCorpusAuthenticationError

FATAL_ERRORS = {
    HypheCorpusAuthenticationError: [
        "Wrong password for corpus!",
        "Don't forget to provide a password for this corpus using --password",
    ]
}


def with_hyphe_fatal_errors(fn):
    return with_fatal_errors(FATAL_ERRORS)(fn)
