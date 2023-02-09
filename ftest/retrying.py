from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
)
from tenacity.wait import wait_base
from minet.web import request_retryer_custom_exponential_backoff
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
    print("Will wait for %s" % format_seconds(retry_state.next_action.sleep))


retryer = Retrying(
    wait=request_retryer_custom_exponential_backoff(exp_base=4),
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
