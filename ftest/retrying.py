from tenacity import (
    Retrying,
    wait_random_exponential,
    retry_if_exception_type,
    stop_after_attempt,
)
from ebbe import format_seconds


def dummy_sleep(retry_state):
    pass


def before(retry_state):
    print("Will call function")


def debug(retry_state):
    print("Will wait for %s" % format_seconds(retry_state.idle_for))


retryer = Retrying(
    wait=wait_random_exponential(exp_base=6, min=10, max=3 * 60 * 60),
    retry=retry_if_exception_type(exception_types=RuntimeError),
    before=before,
    stop=stop_after_attempt(9),
    before_sleep=debug,
    sleep=dummy_sleep,
)


def hellraiser():
    raise RuntimeError


while True:
    retryer(hellraiser)
