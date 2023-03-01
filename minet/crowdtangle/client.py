# =============================================================================
# Minet CrowdTangle API Client
# ================================s=============================================
#
# A unified CrowdTangle API client that can be used to keep an eye on the
# rate limit and the used token etc.
#
import json

from minet.utils import RateLimiterState, rate_limited_method
from minet.web import (
    create_pool_manager,
    create_request_retryer,
    retrying_method,
    request,
)
from minet.crowdtangle.constants import (
    CROWDTANGLE_DEFAULT_TIMEOUT,
    CROWDTANGLE_DEFAULT_RATE_LIMIT,
    CROWDTANGLE_LINKS_DEFAULT_RATE_LIMIT,
)
from minet.crowdtangle.exceptions import (
    CrowdTangleInvalidJSONError,
    CrowdTangleInvalidTokenError,
    CrowdTangleRateLimitExceeded,
    CrowdTangleInvalidRequestError,
    CrowdTangleServerError,
    CrowdTanglePostNotFound,
)
from minet.crowdtangle.leaderboard import crowdtangle_leaderboard
from minet.crowdtangle.lists import crowdtangle_lists
from minet.crowdtangle.post import crowdtangle_post
from minet.crowdtangle.posts import crowdtangle_posts
from minet.crowdtangle.search import crowdtangle_search
from minet.crowdtangle.summary import crowdtangle_summary


class CrowdTangleAPIClient(object):
    def __init__(self, token, rate_limit=None):
        if rate_limit is None:
            rate_limit = CROWDTANGLE_DEFAULT_RATE_LIMIT
            summary_rate_limit = CROWDTANGLE_LINKS_DEFAULT_RATE_LIMIT
        else:
            rate_limit = rate_limit
            summary_rate_limit = rate_limit

        self.token = token
        self.rate_limiter_state = RateLimiterState(rate_limit, period=60)
        self.summary_rate_limiter_state = RateLimiterState(
            summary_rate_limit, period=60
        )
        self.pool_manager = create_pool_manager(timeout=CROWDTANGLE_DEFAULT_TIMEOUT)
        self.retryer = create_request_retryer(
            additional_exceptions=[CrowdTangleInvalidJSONError, CrowdTangleServerError]
        )

    @retrying_method()
    def __request(self, url):
        response = request(url, pool_manager=self.pool_manager, known_encoding="utf-8")

        # Bad auth
        if response.status == 401:
            raise CrowdTangleInvalidTokenError

        # Rate limited
        if response.status == 429:
            raise CrowdTangleRateLimitExceeded

        # Server error
        if response.status >= 500:
            raise CrowdTangleServerError(url=url, status=response.status)

        # Bad params
        if response.status >= 400:
            try:
                data = response.json()
            except json.decoder.JSONDecodeError:
                raise CrowdTangleInvalidRequestError(
                    response.text(), url=url, status=response.status
                )

            raise CrowdTangleInvalidRequestError(
                data["message"], url=url, code=data.get("code"), status=response.status
            )

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            raise CrowdTangleInvalidJSONError

        try:
            return data["result"]
        except KeyError:
            raise CrowdTanglePostNotFound(data=data, url=url)

    @rate_limited_method("rate_limiter_state")
    def request(self, url):
        return self.__request(url)

    @rate_limited_method("summary_rate_limiter_state")
    def request_summary(self, url):
        return self.__request(url)

    def leaderboard(self, **kwargs):
        return crowdtangle_leaderboard(self.request, token=self.token, **kwargs)

    def lists(self, **kwargs):
        return crowdtangle_lists(self.request, token=self.token, **kwargs)

    def post(self, post_id, **kwargs):
        return crowdtangle_post(self.request, post_id, token=self.token, **kwargs)

    def posts(self, sort_by="date", **kwargs):
        return crowdtangle_posts(
            self.request, token=self.token, sort_by=sort_by, **kwargs
        )

    def search(self, terms, sort_by="date", **kwargs):
        return crowdtangle_search(
            self.request, token=self.token, terms=terms, sort_by=sort_by, **kwargs
        )

    def summary(self, link, **kwargs):
        return crowdtangle_summary(
            self.request_summary, link, token=self.token, **kwargs
        )
