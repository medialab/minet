# =============================================================================
# Minet Twitter Exceptions
# =============================================================================
#
from minet.exceptions import MinetError


class TwitterError(MinetError):
    pass


class TwitterGuestTokenError(TwitterError):
    pass


class TwitterPublicAPIQueryTooLongError(TwitterError):
    pass


class TwitterPublicAPIRateLimitError(TwitterError):
    pass


class TwitterPublicAPIInvalidResponseError(TwitterError):
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


class TwitterPublicAPIncompleteTweetIndexError(TwitterError):
    def __init__(self, message=None, tweet_id=None, tweet_index=None):
        super().__init__(message)
        self.tweet_id = tweet_id
        self.tweet_index = tweet_index

    def format_epilog(self):
        epilog = []

        if self.tweet_id is not None:
            epilog.append("Tweet id: %s" % self.tweet_id)

        if self.tweet_index is not None:
            epilog.append("Tweet indexed: %s" % list(self.tweet_index.keys()))

        return ", ".join(epilog) if epilog else ""


class TwitterPublicAPIBadRequest(TwitterError):
    pass


class TwitterPublicAPIOverCapacityError(TwitterError):
    pass


class TwitterPublicAPIParsingError(TwitterError):
    pass


class TwitterPublicAPIHiccupError(TwitterError):
    pass
