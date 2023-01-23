from tenacity import (
    Retrying,
    wait_random_exponential,
    retry_if_exception_type,
    stop_after_attempt,
)
from tenacity.wait import wait_base
from ebbe import format_seconds


class wait_if(wait_base):
    def __init__(self, predicate) -> None:
        super().__init__()
        self.predicate = predicate

    def __call__(self, retry_state):
        if self.predicate(retry_state):
            return 60 * 60
        return 0


def dummy_sleep(retry_state):
    pass


def before(retry_state):
    print("Will call function")


def wait_predicate(retry_state):
    exc = retry_state.outcome.exception()

    return isinstance(exc, RuntimeError)


def debug(retry_state):
    print("Will wait for %s" % format_seconds(retry_state.idle_for))


retryer = Retrying(
    wait=wait_random_exponential(exp_base=6, min=10, max=3 * 60 * 60)
    + wait_if(wait_predicate),
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
