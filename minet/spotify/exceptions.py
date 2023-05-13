# =============================================================================
# Minet Spotify Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class SpotifyError(MinetError):
    pass


class SpotifyServerError(SpotifyError):
    pass


class SpotifyAPINoContentError(SpotifyError):
    """No Content - The request has succeeded but returns no message body."""

    pass


class SpotifyAPIBadRequest(SpotifyError):
    """The request could not be understood by the server due to malformed syntax. The message body will contain more information; see Response Schema."""

    pass


class SpotifyAPIAuthorizationError(SpotifyError):
    """Unauthorized - The request requires user authentication or, if the request included authorization credentials, authorization has been refused for those credentials."""

    pass


class SpotifyTooManyRequestsError(SpotifyError):
    """The Spotify application's rate limit has been reached."""

    pass


class SpotifyInternalServerError(SpotifyError):
    """Spotify's server has an internal error."""

    pass
