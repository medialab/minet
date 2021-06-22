# =============================================================================
# Minet Twitter API Client
# =============================================================================
#
# Twitter public API client.
#
from twitwi import TwitterWrapper

from minet.web import create_request_retryer, retrying_method


class TwitterAPIClient(object):
    def __init__(self, access_token, access_token_secret, api_key, api_secret_key,
                 before_sleep=None):
        self.wrapper = TwitterWrapper(
            access_token,
            access_token_secret,
            api_key,
            api_secret_key
        )
        self.retryer = create_request_retryer(before_sleep=before_sleep)

    @retrying_method()
    def call(self, *args, **kwargs):
        return self.wrapper.call(*args, **kwargs)
