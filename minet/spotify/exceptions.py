# =============================================================================
# Minet Spotify Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class SpotifyAPIError(MinetError):
    def __init__(self, response=None, url=None, status=None):
        message = f"""
URL:
    {url}
RESPONSE:
    {response}
        """
        super().__init__(message)
        self.status = status
