# =============================================================================
# Minet Twitter Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class TwitterError(MinetError):
    pass


class TwitterPublicAPIError(TwitterError):
    pass


class TwitterPublicAPIGuestTokenError(TwitterPublicAPIError):
    pass


class TwitterPublicAPIInvalidCookieError(TwitterPublicAPIError):
    pass


class TwitterPublicAPIQueryTooLongError(TwitterPublicAPIError):
    pass


class TwitterPublicAPIRateLimitError(TwitterPublicAPIError):
    pass


class TwitterPublicAPIBadAuthError(TwitterPublicAPIError):
    def __init__(self, status: int):
        self.status = status
        super().__init__(str(status))


class TwitterPublicAPIInvalidResponseError(TwitterPublicAPIError):
    def __init__(self, message=None, response_text=None, status=None):
        super().__init__(message)
        self.response_text = response_text
        self.status = status

    def format_epilog(self):
        epilog = []

        if self.status is not None:
            epilog.append("Status: %i" % self.status)

        if self.response_text is not None:
            epilog.append("Response: %s" % self.response_text)

        return ", ".join(epilog) if epilog else ""


class TwitterPublicAPIncompleteTweetIndexError(TwitterPublicAPIError):
    def __init__(self, message=None, tweet_id=None, tweet_index=None):
        super().__init__(message)
        self.tweet_id = tweet_id
        self.tweet_index = tweet_index

    def format_epilog(self):
        epilog = []

        if self.tweet_id is not None:
            epilog.append("Tweet id: %s" % self.tweet_id)

        if self.tweet_index is not None:
            epilog.append("Tweets indexed: %s" % list(self.tweet_index.keys()))

        return ", ".join(epilog) if epilog else ""


class TwitterPublicAPIncompleteUserIndexError(TwitterPublicAPIError):
    def __init__(self, message=None, user_id=None, user_index=None):
        super().__init__(message)
        self.user_id = user_id
        self.user_index = user_index

    def format_epilog(self):
        epilog = []

        if self.user_id is not None:
            epilog.append("User id: %s" % self.user_id)

        if self.user_index is not None:
            epilog.append("Users indexed: %s" % list(self.user_index.keys()))

        return ", ".join(epilog) if epilog else ""


class TwitterPublicAPIBadRequest(TwitterPublicAPIError):
    pass


class TwitterPublicAPIOverCapacityError(TwitterPublicAPIError):
    pass


class TwitterPublicAPIParsingError(TwitterPublicAPIError):
    pass


class TwitterPublicAPIHiccupError(TwitterPublicAPIError):
    pass


class TwitterPublicAPINotWorkingAnymore(TwitterPublicAPIError):
    pass
