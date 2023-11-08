# =============================================================================
# Minet YouTube Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class YouTubeError(MinetError):
    pass


class YouTubeInvalidAPIKeyError(YouTubeError):
    pass


class YouTubeAPILimitReached(YouTubeError):
    pass


class YouTubePotentiallyTransientInvalidAPICallError(YouTubeError):
    def __init__(self, url, status, data):
        super().__init__()
        self.url = url
        self.status = status
        self.data = data

    def __str__(self):
        return super().__str__() + ", Url: %s, Status: %i, Data: %s" % (
            self.url,
            self.status,
            self.data,
        )


class YouTubeInvalidAPICallError(YouTubeError):
    def __init__(self, url, status, data):
        super().__init__()
        self.url = url
        self.status = status
        self.data = data

    def __str__(self):
        return super().__str__() + ", Url: %s, Status: %i, Data: %s" % (
            self.url,
            self.status,
            self.data,
        )


class YouTubeInvalidVideoTargetError(YouTubeError):
    pass


class YouTubeInvalidChannelTargetError(YouTubeError):
    pass


class YouTubeDisabledCommentsError(YouTubeError):
    pass


class YouTubeNotFoundError(YouTubeError):
    pass


class YouTubeExclusiveMemberError(YouTubeError):
    pass


class YouTubeUnknown403Error(YouTubeError):
    pass


class YouTubeAccessNotConfiguredError(YouTubeError):
    def __init__(self, message=None, url=None):
        super().__init__(message)
        self.url = url
