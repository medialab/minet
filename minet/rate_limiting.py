from typing import Optional

import time
import functools
from threading import Lock


class RateLimiter:
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
        assert self.last_entry is not None

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
        assert self.last_entry is not None

        running_time = time.perf_counter() - self.last_entry

        delta = self.min_interval - running_time

        if delta > 0:
            time.sleep(delta)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.with_budget:
            return self.exit_with_budget()

        return self.exit()


class RetryableIterator:
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


class RateLimitedIterator:
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


class RateLimiterState:
    def __init__(self, max_per_period: int, period: float = 1.0):
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


class ThreadsafeBurstyRateLimiterState:
    def __init__(self, max_per_period: int, period: float = 1.0):
        self.max_per_period = max_per_period
        self.period = period

        self.current_burst = 0
        self.time_of_next_burst: Optional[float] = None

        self.lock = Lock()

    def wait_if_needed(self):
        while True:
            self.lock.acquire()

            if self.current_burst < self.max_per_period:
                if self.time_of_next_burst is None:
                    self.time_of_next_burst = time.perf_counter() + self.period

                self.current_burst += 1
                self.lock.release()
                return

            assert self.time_of_next_burst is not None

            delta = self.time_of_next_burst - time.perf_counter()

            self.time_of_next_burst = None
            self.current_burst = 0

            if delta > 0:
                time.sleep(delta)
                self.lock.release()
                continue
            else:
                self.lock.release()
                return

    # NOTE: noop
    def update(self):
        pass


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


def rate_limited_method(attr: str = "rate_limiter_state"):
    def decorate(fn):
        @functools.wraps(fn)
        def decorated(self, *args, **kwargs):
            state = getattr(self, attr)

            if not isinstance(
                state, (RateLimiterState, ThreadsafeBurstyRateLimiterState)
            ):
                raise ValueError

            state.wait_if_needed()
            result = fn(self, *args, **kwargs)
            state.update()

            return result

        return decorated

    return decorate
