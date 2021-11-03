# =============================================================================
# Minet BuzzSumo API Client
# =============================================================================
#
# BuzzSumo API client.
#
from json import JSONDecodeError
from urllib.parse import quote

from minet.utils import RateLimiterState, rate_limited_method
from minet.web import (
    create_request_retryer,
    retrying_method,
    request_json
)

from minet.buzzsumo.exceptions import (
    BuzzSumoInvalidTokenError,
    BuzzSumoOutageError,
    BuzzSumoBadRequestError
)

URL_TEMPLATE = 'https://api.buzzsumo.com%s?api_key=%s'


def construct_url(endpoint, token, begin_date=None, end_date=None,
                  num_results=100, q=None, page=None):

    url = URL_TEMPLATE % (endpoint, token)

    url += '&num_results=%i' % num_results

    if begin_date:
        url += '&begin_date=%s' % begin_date
    if end_date:
        url += '&end_date=%s' % (end_date - 1)
    if q is not None:
        url += '&q=%s' % quote(q)
    if page is not None:
        url += '&page=%i' % page

    return url


class BuzzSumoAPIClient(object):
    def __init__(self, token):
        self.token = token
        self.retryer = create_request_retryer(
            additional_exceptions=[BuzzSumoOutageError]
        )

        # 10 calls per ~12s
        self.rate_limiter_state = RateLimiterState(10, 12)

    @retrying_method()
    @rate_limited_method()
    def request(self, url):

        try:
            err, response, data = request_json(url)
        except JSONDecodeError:
            raise BuzzSumoBadRequestError

        if err:
            raise err

        if response.status == 401:
            raise BuzzSumoInvalidTokenError

        if response.status == 500:
            raise BuzzSumoBadRequestError

        if response.status > 500:
            raise BuzzSumoOutageError

        return response, data

    def limit(self):
        url = construct_url(
            '/search/articles.json',
            token=self.token,
            q='fake news',
            num_results=1
        )

        response, _ = self.request(url)

        return response.headers['X-RateLimit-Month-Remaining']
