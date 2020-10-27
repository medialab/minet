# =============================================================================
# Minet CrowdTangle Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the CrowdTangle namespace.
#
import json
from datetime import date, datetime, timedelta

from minet.utils import request, rate_limited_from_state
from minet.crowdtangle.constants import (
    CROWDTANGLE_OUTPUT_FORMATS
)
from minet.crowdtangle.exceptions import (
    CrowdTangleMissingStartDateError,
    CrowdTangleInvalidTokenError,
    CrowdTangleInvalidRequestError,
    CrowdTangleInvalidJSONError,
    CrowdTangleRateLimitExceeded
)

DAY_DELTA = timedelta(days=1)


def day_range(end):
    day_delta = timedelta(days=1)

    start_date = date(*[int(i) for i in end.split('-')])
    current_date = date.today() + day_delta

    while start_date != current_date:
        end_date = current_date
        current_date -= day_delta

        yield current_date.isoformat(), end_date.isoformat()


def years_iter(start_date, end_date):
    current_year = int(end_date[:4])
    target_year = int(start_date[:4])

    current_start_date = str(current_year) + '-01-01T00:00:00'
    current_end_date = end_date

    while current_year > target_year:
        yield current_start_date, current_end_date

        current_year -= 1
        current_end_date = str(current_year) + '-12-31T23:59:59'
        current_start_date = str(current_year) + current_start_date[4:]

    yield start_date, current_end_date


def infer_end_date():
    return datetime.now().isoformat(timespec='seconds')


def get_last_day_of_month(year, month):
    d = 31

    while d > 27:
        try:
            attempt = date(int(year), int(month), d)
            return attempt.isoformat()[8:10]
        except ValueError:
            d -= 1

    raise TypeError('could not find last day of month')


def complement_date(d, bound):
    if len(d) == 4:
        d += '-'
        d += '01' if bound == 'start' else '12'

    if len(d) == 7:
        d += '-'
        d += '01' if bound == 'start'else get_last_day_of_month(d[:4], d[5:7])

    if len(d) == 10:
        d += 'T00:00:00' if bound == 'start' else 'T23:59:59'

    return d


# TODO: __call__ should receive a status to make finer decisions
class PartitionStrategyNoop(object):
    def __init__(self, kwargs, url_forge):
        self.kwargs = kwargs
        self.url_forge = url_forge
        self.started = False

    def __call__(self, items):
        if not self.started:
            self.started = True
            return self.url_forge(**self.kwargs)

        return None

    def get_detail(self):
        return None

    def should_go_next(self, items):
        return True


class PartitionStrategyLimit(PartitionStrategyNoop):
    def __init__(self, kwargs, url_forge, limit):
        self.kwargs = kwargs
        self.url_forge = url_forge
        self.last_item = None
        self.seen = 0
        self.shifts = 0
        self.limit = limit
        self.started = False

        self.years = years_iter(self.kwargs['start_date'], self.kwargs['end_date'])
        self.rotate_year()

    def rotate_year(self):
        try:
            start_date, end_date = next(self.years)
            self.kwargs['start_date'] = start_date
            self.kwargs['end_date'] = end_date
        except StopIteration:
            return False

        return True

    def __call__(self, items):
        if not self.started:
            self.started = True
            return self.url_forge(**self.kwargs)

        if items is None:
            could_rotate = self.rotate_year()

            if not could_rotate:
                return None

            return self.url_forge(**self.kwargs)

        if self.last_item is not None:
            self.kwargs['end_date'] = self.last_item['date'].replace(' ', 'T')

        return self.url_forge(**self.kwargs)

    def get_detail(self):
        if 'end_date' in self.kwargs:
            return {'date': self.kwargs['end_date'], 'shifts': self.shifts}

    def should_go_next(self, items):
        n = len(items)

        if n > 0:
            self.last_item = items[-1]
            self.seen += n

        if self.seen >= self.limit:
            self.seen = 0
            self.shifts += 1
            return False

        return True


def step(http, url, item_key):
    err, result = request(http, url)

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
        data = json.loads(result.data.decode('utf-8'))
        raise CrowdTangleInvalidRequestError(data['message'], code=data['code'], status=result.status)

    try:
        data = json.loads(result.data)['result']
    except:
        raise CrowdTangleInvalidJSONError

    items = None

    if item_key in data:
        items = data[item_key]

        if len(items) == 0:
            items = None

    # Extracting next link
    pagination = data['pagination']
    next_page = pagination['nextPage'] if 'nextPage' in pagination else None

    return items, next_page


def default_item_id_getter(item):
    return item['id']


def make_paginated_iterator(url_forge, item_key, formatter,
                            item_id_getter=default_item_id_getter):

    def create_iterator(http, token, rate_limiter_state, partition_strategy=None,
                        limit=None, format='csv_dict_row', per_call=False, detailed=False,
                        namespace=None, **kwargs):

        if format not in CROWDTANGLE_OUTPUT_FORMATS:
            raise TypeError('minet.crowdtangle: unkown `format`.')

        if namespace is not None:
            kwargs = vars(namespace)
        else:
            kwargs['token'] = token

        # Checking we have the necessary dates
        if kwargs.get('sort_by', 'date') == 'date':
            if kwargs.get('start_date') is None:
                raise CrowdTangleMissingStartDateError

            # Inferring end date to be now, this will be important later
            if kwargs.get('end_date') is None:
                kwargs['end_date'] = infer_end_date()

        # Complementing dates
        if kwargs.get('start_date') is not None:
            kwargs['start_date'] = complement_date(kwargs['start_date'], 'start')

        if kwargs.get('end_date') is not None:
            kwargs['end_date'] = complement_date(kwargs['end_date'], 'end')

        N = 0
        C = 0
        url = url_forge(**kwargs)
        last_url = None
        last_items = set()

        has_limit = limit is not None

        rate_limited_step = rate_limited_from_state(rate_limiter_state)(step)

        while True:
            C += 1

            items, next_url = rate_limited_step(http, url, item_key)

            # We have exhausted the available data
            if items is None:
                # TODO: rotate
                break

            enough_to_stop = False
            n = 0

            last_url = url

            acc = []

            for item in items:

                # Avoiding duplicating items due to race conditions
                if item_id_getter(item) in last_items:
                    continue

                n += 1
                N += 1

                if format == 'csv_dict_row':
                    item = formatter(item, as_dict=True)
                elif format == 'csv_row':
                    item = formatter(item)

                acc.append(item)

                if has_limit and N >= limit:
                    enough_to_stop = True
                    break

            if per_call:
                if detailed:
                    # TODO: furbish
                    yield None, acc
                else:
                    yield acc
            else:
                yield from acc

            if enough_to_stop:
                break

            # We need to track last items to avoid registering the same one twice
            last_items = set(item_id_getter(item) for item in items)

            # Paginating
            if next_url is None:
                # TODO: rotate
                break

            url = next_url

    return create_iterator
