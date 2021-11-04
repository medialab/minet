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

from minet.buzzsumo.formatters import format_article
from minet.buzzsumo.exceptions import (
    BuzzSumoInvalidTokenError,
    BuzzSumoOutageError,
    BuzzSumoBadRequestError,
    BuzzSumoInvalidQueryError
)

URL_TEMPLATE = 'https://api.buzzsumo.com%s?api_key=%s'
MAXIMUM_PAGE_NB = 98


def construct_url(endpoint, token, begin_timestamp=None, end_timestamp=None,
                  num_results=100, q=None, page=None):

    url = URL_TEMPLATE % (endpoint, token)

    url += '&num_results=%i' % num_results

    if begin_timestamp:
        url += '&begin_date=%s' % begin_timestamp
    if end_timestamp:
        url += '&end_date=%s' % (end_timestamp - 1)
    if q is not None:
        url += '&q=%s' % quote(q)
    if page is not None:
        url += '&page=%i' % page

    return url


def optimize_period_timestamps_wrt_nb_pages(period_timestamps, nb_pages, maximum_page_nb):
    new_period_timestamps = period_timestamps

    if any(nb_page > maximum_page_nb for nb_page in nb_pages):
        for i in range(len(nb_pages)):
            if nb_pages[i] > maximum_page_nb:
                new_period_timestamps.append((period_timestamps[i] + period_timestamps[i + 1]) / 2)

        new_period_timestamps.sort()

    return period_timestamps


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

        if response.status == 406:
            raise BuzzSumoInvalidQueryError(data.get('error'), url=url, data=data)

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

    def domain_summary(self, domain, begin_timestamp, end_timestamp):
        url = construct_url(
            '/search/articles.json',
            token=self.token,
            q=domain,
            begin_timestamp=begin_timestamp,
            end_timestamp=end_timestamp
        )

        _, data = self.request(url)

        return {
            'total_results': int(data['total_results']),
            'total_pages': data['total_pages']
        }

    def __get_nb_pages_per_period_dates(self, domain, period_timestamps):
        nb_pages = []

        for i in range(len(period_timestamps) - 1):
            info = self.domain_summary(
                domain,
                begin_timestamp=period_timestamps[i],
                end_timestamp=period_timestamps[i + 1]
            )

            nb_pages.append(info['total_pages'])

        return nb_pages

    def domain_articles(self, domain, begin_timestamp, end_timestamp):

        # Here we optimize the periods used to request the API, because BuzzSumo
        # prevents us from getting more than 99 pages.
        maximum_page_nb = MAXIMUM_PAGE_NB
        period_timestamps = [begin_timestamp, end_timestamp]
        nb_pages = [1000]

        # This loop creates adapted time periods that all return less than 99 pages of results:
        while any(nb_page > maximum_page_nb for nb_page in nb_pages):

            # We ask how many pages are needed to get all the articles for the given periods:
            nb_pages = self.__get_nb_pages_per_period_dates(domain, period_timestamps)

            # If a given period gets more than 98 pages, this period is then cut down in half:
            period_timestamps = optimize_period_timestamps_wrt_nb_pages(period_timestamps, nb_pages, maximum_page_nb)

        # Now we get all the results for the optimized periods
        for i in range(len(period_timestamps) - 1):
            page = 0

            while True:
                url = construct_url(
                    '/search/articles.json',
                    token=self.token,
                    q=domain,
                    begin_timestamp=period_timestamps[i],
                    end_timestamp=period_timestamps[i + 1],
                    page=page
                )

                _, data = self.request(url)

                if not data['results']:
                    break

                for article in data['results']:
                    yield format_article(article)

                page += 1
