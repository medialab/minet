from urllib3.exceptions import (
    ConnectTimeoutError,
    ReadTimeoutError,
    SSLError,
    NewConnectionError,
    ProtocolError,
    DecodeError,
    LocationValueError,
    LocationParseError,
)

from minet.exceptions import (
    UnknownEncodingError,
    InvalidURLError,
    MaxRedirectsError,
    InfiniteRedirectsError,
    SelfRedirectError,
    InvalidRedirectError,
    BadlyEncodedLocationHeaderError,
    TrafilaturaError,
    FilenameFormattingError,
    FinalTimeoutError,
    CouldNotInferEncodingError,
    InvalidStatusError,
)


def serialize_new_connection_error(error):
    msg = repr(error).lower()

    if "no route to host" in msg or "errno 113" in msg:
        return "no-route-to-host"

    if "name or service not known" in msg or "errno 8" in msg:
        return "unknown-host"

    if "connection refused" in msg:
        return "connection-refused"

    if "temporary failure in name resolution" in msg or "errno -3" in msg:
        return "name-resolution-failure"

    if "no address associated with hostname" in msg or "errno -5" in msg:
        return "no-address-associated-with-hostname"

    if "network is unreachable" in msg or "errno 101" in msg:
        return "unreachable-network"

    return "new-connection-error"


def serialize_protocol_error(error):
    msg = repr(error).lower()

    if "connection aborted" in msg:
        return "connection-aborted"

    if "connection refused" in msg:
        return "connection-refused"

    return "connection-error"


def serialize_decode_error(error):
    msg = repr(error)

    if "gzip" in msg:
        return "invalid-gzip"

    return "invalid-encoding"


def serialize_invalid_status_error(error: InvalidStatusError):
    return "invalid-status-%i" % error.status


ERROR_REPORTERS = {
    UnicodeDecodeError: "wrong-encoding",
    UnknownEncodingError: "unknown-encoding",
    FileNotFoundError: "file-not-found",
    InvalidURLError: "invalid-url",
    LocationValueError: "invalid-url",
    LocationParseError: "invalid-url",
    SSLError: "ssl",
    NewConnectionError: serialize_new_connection_error,
    ProtocolError: serialize_protocol_error,
    ConnectTimeoutError: "connect-timeout",
    ReadTimeoutError: "read-timeout",
    FinalTimeoutError: "final-timeout",
    MaxRedirectsError: "max-redirects",
    InfiniteRedirectsError: "infinite-redirects",
    SelfRedirectError: "self-redirect",
    InvalidRedirectError: "invalid-redirect",
    BadlyEncodedLocationHeaderError: "badly-encoded-location",
    DecodeError: serialize_decode_error,
    TrafilaturaError: "trafilatura-error",
    FilenameFormattingError: "filename-formatting-error",
    CouldNotInferEncodingError: "could-not-infer-encoding",
    InvalidStatusError: serialize_invalid_status_error,
}


def serialize_error_as_slug(error: BaseException):
    reporter = ERROR_REPORTERS.get(type(error), repr)

    return reporter(error) if callable(reporter) else reporter
