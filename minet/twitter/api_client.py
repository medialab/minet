# =============================================================================
# Minet Twitter API Client
# =============================================================================
#
# Twitter public API client.
#
from json import JSONDecodeError
from twitwi import TwitterWrapper
from twitwi.exceptions import (
    TwitterWrapperMaxAttemptsExceeded,
    TwitterPayloadV2IncompleteIncludesError,
)
from twitter import TwitterError

from minet.web import create_request_retryer, retrying_method


def retryer_predicate(exc):
    if isinstance(
        exc,
        (
            JSONDecodeError,
            TwitterWrapperMaxAttemptsExceeded,
            TwitterPayloadV2IncompleteIncludesError,
        ),
    ):
        return True

    if not isinstance(exc, TwitterError):
        return False

    msg = str(exc).lower()

    # Retrying if we actually caught a json decoding error
    # TODO: simplify this if the `twitter` lib changes its error inheritance scheme
    if "incomplete json data collected" in msg:
        return True

    return False


class TwitterAPIClient(object):
    def __init__(
        self,
        access_token,
        access_token_secret,
        api_key,
        api_secret_key,
        api_version="1.1",
    ):
        self.retryer = create_request_retryer(predicate=retryer_predicate)

        self.wrapper = self.retryer(
            TwitterWrapper,
            access_token,
            access_token_secret,
            api_key,
            api_secret_key,
            api_version=api_version,
        )

    @retrying_method()
    def call(self, *args, **kwargs):
        return self.wrapper.call(*args, **kwargs)
