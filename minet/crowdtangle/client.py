# =============================================================================
# Minet CrowdTangle API Client
# =============================================================================
#
# A unified CrowdTangle API client that can be used to keep an eye on the
# rate limit and the used token etc.
#
from minet.utils import (
    create_pool,
    RateLimiterState,
    rate_limited_method
)
from minet.crowdtangle.constants import (
    CROWDTANGLE_DEFAULT_TIMEOUT,
    CROWDTANGLE_DEFAULT_RATE_LIMIT,
    CROWDTANGLE_LINKS_DEFAULT_RATE_LIMIT
)
from minet.crowdtangle.leaderboard import crowdtangle_leaderboard
from minet.crowdtangle.lists import crowdtangle_lists
from minet.crowdtangle.post import crowdtangle_post
from minet.crowdtangle.posts import crowdtangle_posts
from minet.crowdtangle.search import crowdtangle_search
from minet.crowdtangle.summary import crowdtangle_summary


class CrowdTangleClient(object):
    def __init__(self, token, rate_limit=None):
        if rate_limit is None:
            rate_limit = CROWDTANGLE_DEFAULT_RATE_LIMIT
            summary_rate_limit = CROWDTANGLE_LINKS_DEFAULT_RATE_LIMIT
        else:
            rate_limit = rate_limit
            summary_rate_limit = rate_limit

        self.token = token
        self.rate_limiter_state = RateLimiterState(rate_limit, period=60)
        self.summary_rate_limiter_state = RateLimiterState(summary_rate_limit, period=60)
        self.http = create_pool(timeout=CROWDTANGLE_DEFAULT_TIMEOUT)

    def leaderboard(self, **kwargs):
        return crowdtangle_leaderboard(
            self.http,
            token=self.token,
            rate_limiter_state=self.rate_limiter_state,
            **kwargs
        )

    @rate_limited_method('rate_limiter_state')
    def lists(self, **kwargs):
        return crowdtangle_lists(
            self.http,
            token=self.token,
            **kwargs
        )

    @rate_limited_method('rate_limiter_state')
    def post(self, post_id, **kwargs):
        return crowdtangle_post(
            self.http,
            post_id,
            token=self.token,
            **kwargs
        )

    def posts(self, **kwargs):
        return crowdtangle_posts(
            self.http,
            token=self.token,
            rate_limiter_state=self.rate_limiter_state,
            **kwargs
        )

    def search(self, terms, **kwargs):
        return crowdtangle_search(
            self.http,
            token=self.token,
            rate_limiter_state=self.rate_limiter_state,
            terms=terms,
            **kwargs
        )

    @rate_limited_method('summary_rate_limiter_state')
    def summary(self, link, **kwargs):
        return crowdtangle_summary(
            self.http,
            link,
            token=self.token,
            **kwargs
        )
