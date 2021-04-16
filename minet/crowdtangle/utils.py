# =============================================================================
# Minet CrowdTangle Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the CrowdTangle namespace.
#
import json
from datetime import date, datetime, timedelta

from minet.utils import rate_limited_from_state
from minet.web import request, create_request_retryer
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


def step(pool, url, item_key):
    err, result = request(url, pool=pool)

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

    def create_iterator(pool, token, rate_limiter_state, limit=None,
                        raw=False, per_call=False, detailed=False,
                        namespace=None, before_sleep=None, **kwargs):

        if namespace is not None:
            kwargs = vars(namespace)
        else:
            kwargs['token'] = token

        # Checking we have the necessary dates
        if kwargs.get('sort_by') == 'date':
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
        last_url = None
        last_items = set()

        has_limit = limit is not None

        rate_limited_step = rate_limited_from_state(rate_limiter_state)(step)

        retryer = create_request_retryer(
            additional_exceptions=[CrowdTangleRateLimitExceeded, CrowdTangleInvalidJSONError],
            before_sleep=before_sleep
        )

        # Chunking
        need_to_chunk = kwargs.get('sort_by') == 'date'
        chunk_size = kwargs.get('chunk_size', 500)
        current_chunk_size = 0
        shifts = 0
        years = years_iter(kwargs['start_date'], kwargs['end_date']) if need_to_chunk else None

        def rotate_year():
            try:
                start_date, end_date = next(years)
                kwargs['start_date'] = start_date
                kwargs['end_date'] = end_date
            except StopIteration:
                return False

            return True

        if need_to_chunk:
            rotate_year()

        # Starting url
        url = url_forge(**kwargs)

        while True:
            C += 1

            items, next_url = retryer(rate_limited_step, pool, url, item_key)

            # We have exhausted the available data
            if items is None:

                if need_to_chunk:
                    could_rotate = rotate_year()

                    if could_rotate:
                        url = url_forge(**kwargs)
                        continue

                break

            enough_to_stop = False
            n = 0

            last_url = url

            acc = []

            for item in items:

                # Avoiding duplicating items due to race conditions
                if item_id_getter(item) in last_items:
                    continue

                current_date = item.get('date')

                n += 1
                N += 1
                current_chunk_size += 1

                if not raw:
                    item = formatter(item)

                acc.append(item)

                if has_limit and N >= limit:
                    enough_to_stop = True
                    break

            if per_call:
                if detailed:
                    details = None

                    if need_to_chunk:
                        details = {
                            'date': current_date,
                            'shifts': shifts
                        }

                    yield details, acc
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
                if need_to_chunk:
                    could_rotate = rotate_year()

                    if could_rotate:
                        url = url_forge(**kwargs)
                        continue

                break

            # Handling chunking
            if need_to_chunk and current_chunk_size >= chunk_size:
                current_chunk_size = 0
                shifts += 1
                kwargs['end_date'] = items[-1]['date'].replace(' ', 'T')
                url = url_forge(**kwargs)
                continue

            url = next_url

    return create_iterator
