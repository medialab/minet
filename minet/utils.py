# =============================================================================
# Minet Utils
# =============================================================================
#
# Miscellaneous helper function used throughout the library.
#
import re
import hashlib
import json
import yaml
import time
import string
import functools
import dateparser
from random import uniform

from minet.exceptions import DefinitionInvalidFormatError


def fuzzy_int(value):
    try:
        return int(value)
    except ValueError:
        return int(float(value))


def md5(string):
    h = hashlib.md5()
    h.update(string.encode())
    return h.hexdigest()


DOUBLE_QUOTES_RE = re.compile(r'"')


def fix_ensure_ascii_json_string(s):
    try:
        return json.loads('"%s"' % DOUBLE_QUOTES_RE.sub('\\"', s))
    except json.decoder.JSONDecodeError:
        return s


class RateLimiter(object):
    """
    Naive rate limiter context manager with smooth output.

    Note that it won't work in a multi-threaded environment.

    Args:
        max_per_period (int): Maximum number of calls per period.
        period (float): Duration of a period in seconds. Defaults to 1.0.

    """

    def __init__(self, max_per_period, period=1.0, with_budget=False):
        max_per_second = max_per_period / period
        self.min_interval = 1.0 / max_per_second
        self.max_budget = period / 4
        self.budget = 0.0
        self.last_entry = None
        self.with_budget = with_budget

    def enter(self):
        self.last_entry = time.perf_counter()

    def __enter__(self):
        return self.enter()

    def exit_with_budget(self):
        running_time = time.perf_counter() - self.last_entry

        delta = self.min_interval - running_time

        # Consuming budget
        if delta >= self.budget:
            delta -= self.budget
            self.budget = 0
        else:
            self.budget -= delta
            delta = 0

        # Do we need to sleep?
        if delta > 0:
            time.sleep(delta)
        elif delta < 0:
            self.budget -= delta

        # Clamping budget
        # TODO: this should be improved by a circular buffer of last calls
        self.budget = min(self.budget, self.max_budget)

    def exit(self):
        running_time = time.perf_counter() - self.last_entry

        delta = self.min_interval - running_time

        if delta > 0:
            time.sleep(delta)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.with_budget:
            return self.exit_with_budget()

        return self.exit()


class RetryableIterator(object):
    """
    Iterator exposing a #.retry method that will make sure the next item
    is the same as the current one.
    """

    def __init__(self, iterator):
        self.iterator = iter(iterator)
        self.current_value = None
        self.retried = False
        self.retries = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.retried:
            self.retried = False
            return self.current_value

        self.retries = 0
        self.current_value = next(self.iterator)
        return self.current_value

    def retry(self):
        self.retries += 1
        self.retried = True


class RateLimitedIterator(object):
    """
    Handy iterator wrapper that will yield its items while respecting a given
    rate limit and that will not sleep needlessly when the iterator is
    finally fully consumed.
    """

    def __init__(self, iterator, max_per_period, period=1.0):
        self.iterator = RetryableIterator(iterator)
        self.rate_limiter = RateLimiter(max_per_period, period)
        self.empty = False

        try:
            self.next_value = next(self.iterator)
        except StopIteration:
            self.next_value = None
            self.empty = True

    @property
    def retries(self):
        return self.iterator.retries

    def retry(self):
        return self.iterator.retry()

    def __iter__(self):
        if self.empty:
            return

        while True:
            self.rate_limiter.enter()

            yield self.next_value

            # NOTE: if the iterator is fully consumed, this will raise StopIteration
            # and skip the exit part that could sleep needlessly
            try:
                self.next_value = next(self.iterator)
            except StopIteration:
                return

            self.rate_limiter.exit()


class RateLimiterState(object):
    def __init__(self, max_per_period, period=1.0):
        max_per_second = max_per_period / period
        self.min_interval = 1.0 / max_per_second
        self.last_entry = None

    def wait_if_needed(self):
        if self.last_entry is None:
            return

        running_time = time.perf_counter() - self.last_entry
        delta = self.min_interval - running_time

        if delta > 0:
            time.sleep(delta)

    def update(self):
        self.last_entry = time.perf_counter()


def rate_limited(max_per_period, period=1.0):
    state = RateLimiterState(max_per_period, period)

    def decorate(fn):

        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            state.wait_if_needed()
            result = fn(*args, **kwargs)
            state.update()

            return result

        return decorated

    return decorate


def rate_limited_from_state(state):
    def decorate(fn):

        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            state.wait_if_needed()
            result = fn(*args, **kwargs)
            state.update()

            return result

        return decorated

    return decorate


def rate_limited_method(attr='rate_limiter_state'):
    def decorate(fn):

        @functools.wraps(fn)
        def decorated(self, *args, **kwargs):
            state = getattr(self, attr)

            if not isinstance(state, RateLimiterState):
                raise ValueError

            state.wait_if_needed()
            result = fn(self, *args, **kwargs)
            state.update()

            return result

        return decorated

    return decorate


class PseudoFStringFormatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        result = eval(field_name, None, kwargs)

        return result, None


def load_definition(f, encoding='utf-8'):
    string_path = isinstance(f, str)

    if string_path:
        path = f
        f = open(path, encoding=encoding)
    else:
        path = f.name

    if path.endswith('.json'):
        definition = json.load(f)

    elif path.endswith('.yml') or path.endswith('.yaml'):
        definition = yaml.safe_load(f)

    else:
        raise DefinitionInvalidFormatError

    if string_path:
        f.close()

    return definition


def sleep_with_entropy(seconds, max_random_addendum):
    random_addendum = uniform(0, max_random_addendum)
    time.sleep(seconds + random_addendum)


INTERVALS = [
    ('weeks', 60 * 60 * 24 * 7),  # 60 * 60 * 24 * 7
    ('days', 60 * 60 * 24),    # 60 * 60 * 24
    ('hours', 60 * 60),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1)
]


def prettyprint_integer(n):
    return '{:,}'.format(int(n))


def prettyprint_seconds(seconds, granularity=None):
    result = []

    for name, count in INTERVALS:
        value = seconds // count

        if value:
            seconds -= value * count

            if value == 1:
                name = name.rstrip('s')

            result.append('%i %s' % (value, name))

    if not result:
        return '%.2f seconds' % seconds

    if granularity is not None:
        result = result[:granularity]

    return ', '.join(result)


def parse_date(formatted_date, lang='en'):
    if not isinstance(formatted_date, str):
        raise TypeError

    parsed = dateparser.parse(
        formatted_date,
        languages=[lang]
    )

    if not parsed:
        return None

    return parsed.isoformat().split('.', 1)[0]


def is_binary_mimetype(m: str) -> bool:
    if m.startswith('text/'):
        return False

    if not m.startswith('application/'):
        return True

    second_part = m.split('/', 1)[-1]

    return not (
        'json' in second_part or
        'html' in second_part or
        'xml' in second_part or
        'yaml' in second_part or
        'yml' in second_part or
        second_part == 'x-httpd-php'
    )
