# =============================================================================
# Minet CLI Reporters
# =============================================================================
#
# Various reporters whose goal is to convert errors etc. into human-actionable
# labels in CSV format, for instance.
#
from urllib3.exceptions import (
    ConnectTimeoutError,
    MaxRetryError,
    ReadTimeoutError,
    ResponseError,
    SSLError,
    NewConnectionError,
    ProtocolError
)

from minet.exceptions import (
    UnknownEncodingError,
    InvalidURLError
)


def max_retry_error_reporter(error):
    if isinstance(error, ConnectTimeoutError):
        return 'connect-timeout'

    if isinstance(error, ReadTimeoutError):
        return 'read-timeout'

    if isinstance(error.reason, ResponseError) and 'redirect' in repr(error.reason):
        return 'too-many-redirects'

    return 'max-retries-exceeded'


def new_connection_error_reporter(error):
    msg = repr(error)

    if 'Name or service not known' in msg:
        return 'unknown-dns'

    return msg


def protocol_error_reporter(error):
    msg = repr(error)

    if 'Connection aborted' in msg:
        return 'connection-aborted'

    return msg


ERROR_REPORTERS = {
    UnicodeDecodeError: 'wrong-encoding',
    UnknownEncodingError: 'unknown-encoding',
    MaxRetryError: max_retry_error_reporter,
    InvalidURLError: 'invalid-url',
    SSLError: 'ssl',
    NewConnectionError: new_connection_error_reporter,
    ProtocolError: protocol_error_reporter,
    ConnectTimeoutError: 'connect-timeout',
    ReadTimeoutError: 'read-timeout'
}


def report_error(error):
    reporter = ERROR_REPORTERS.get(type(error), repr)

    return reporter(error) if callable(reporter) else reporter
