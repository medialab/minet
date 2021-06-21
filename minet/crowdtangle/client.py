# =============================================================================
# Minet CrowdTangle API Client
# =============================================================================
#
# A unified CrowdTangle API client that can be used to keep an eye on the
# rate limit and the used token etc.
#
import json

from minet.utils import (
    RateLimiterState,
    rate_limited_method
)
from minet.web import (
    create_pool,
    create_request_retryer,
    retrying_method,
    request
)
from minet.crowdtangle.constants import (
    CROWDTANGLE_DEFAULT_TIMEOUT,
    CROWDTANGLE_DEFAULT_RATE_LIMIT,
    CROWDTANGLE_LINKS_DEFAULT_RATE_LIMIT
)
from minet.crowdtangle.exceptions import (
    CrowdTangleInvalidJSONError,
    CrowdTangleInvalidTokenError,
    CrowdTangleRateLimitExceeded,
    CrowdTangleInvalidRequestError
)
from minet.crowdtangle.leaderboard import crowdtangle_leaderboard
from minet.crowdtangle.lists import crowdtangle_lists
from minet.crowdtangle.post import crowdtangle_post
from minet.crowdtangle.posts import crowdtangle_posts
from minet.crowdtangle.search import crowdtangle_search
from minet.crowdtangle.summary import crowdtangle_summary


class CrowdTangleAPIClient(object):
    def __init__(self, token, rate_limit=None, before_sleep=None):
        if rate_limit is None:
            rate_limit = CROWDTANGLE_DEFAULT_RATE_LIMIT
            summary_rate_limit = CROWDTANGLE_LINKS_DEFAULT_RATE_LIMIT
        else:
            rate_limit = rate_limit
            summary_rate_limit = rate_limit

        self.token = token
        self.rate_limiter_state = RateLimiterState(rate_limit, period=60)
        self.summary_rate_limiter_state = RateLimiterState(summary_rate_limit, period=60)
        self.pool = create_pool(timeout=CROWDTANGLE_DEFAULT_TIMEOUT)
        self.retryer = create_request_retryer(
            additional_exceptions=[CrowdTangleInvalidJSONError],
            before_sleep=before_sleep
        )

    @retrying_method()
    def __request(self, url):
        err, result = request(url, pool=self.pool)

        # Debug
        if err:
            raise err

        # Bad auth
        if result.status == 401:
            raise CrowdTangleInvalidTokenError

        elif result.status == 429:
            raise CrowdTangleRateLimitExceeded

        # Bad params
        if result.status >= 400:
            data = result.data.decode('utf-8')

            try:
                data = json.loads(data)
            except:
                raise CrowdTangleInvalidRequestError(data)

            raise CrowdTangleInvalidRequestError(data['message'], code=data['code'], status=result.status)

        try:
            data = json.loads(result.data)['result']
        except (json.decoder.JSONDecodeError, TypeError, KeyError):
            raise CrowdTangleInvalidJSONError

        return data

    @rate_limited_method('rate_limiter_state')
    def request(self, url):
        return self.__request(url)

    @rate_limited_method('summary_rate_limiter_state')
    def request_summary(self, url):
        return self.__request(url)

    def leaderboard(self, **kwargs):
        return crowdtangle_leaderboard(
            self.pool,
            token=self.token,
            rate_limiter_state=self.rate_limiter_state,
            **kwargs
        )

    @rate_limited_method('rate_limiter_state')
    def lists(self, **kwargs):
        return crowdtangle_lists(
            self.pool,
            token=self.token,
            **kwargs
        )

    @rate_limited_method('rate_limiter_state')
    def post(self, post_id, **kwargs):
        return crowdtangle_post(
            self.pool,
            post_id,
            token=self.token,
            **kwargs
        )

    def posts(self, sort_by='date', **kwargs):
        return crowdtangle_posts(
            self.pool,
            token=self.token,
            rate_limiter_state=self.rate_limiter_state,
            sort_by=sort_by,
            **kwargs
        )

    def search(self, terms, sort_by='date', **kwargs):
        return crowdtangle_search(
            self.pool,
            token=self.token,
            rate_limiter_state=self.rate_limiter_state,
            terms=terms,
            sort_by=sort_by,
            **kwargs
        )

    def summary(self, link, **kwargs):
        return crowdtangle_summary(
            self.request_summary,
            link,
            token=self.token,
            **kwargs
        )
