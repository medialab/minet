# =============================================================================
# Minet Twitter API Client
# =============================================================================
#
# Twitter public API client.
#
from json import JSONDecodeError
from twitwi import TwitterWrapper
from twitter import TwitterError

from minet.web import create_request_retryer, retrying_method


def catch_json_error(exc):
    if isinstance(exc, JSONDecodeError):
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
        before_sleep=None,
    ):
        self.wrapper = TwitterWrapper(
            access_token,
            access_token_secret,
            api_key,
            api_secret_key,
            api_version=api_version,
        )
        self.retryer = create_request_retryer(
            before_sleep=before_sleep, predicate=catch_json_error
        )

    @retrying_method()
    def call(self, *args, **kwargs):
        return self.wrapper.call(*args, **kwargs)
