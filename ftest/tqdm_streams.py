import time
import sys
from tqdm import tqdm
from tqdm.contrib import DummyTqdmFile
from contextlib import redirect_stdout, contextmanager
from minet.cli.utils import LoadingBar, tqdm_stdout_stderr, print_err


@contextmanager
def print_as_tqdm_write():
    original_print = __builtins__.print

    try:
        __builtins__.print = tqdm.write
        yield
    finally:
        __builtins__.print = original_print


def work(n=100):
    bar = LoadingBar("Processing", total=n)

    for _ in range(n):
        bar.update()
        print("something")
        print_err("something else")
        time.sleep(0.1)


with print_as_tqdm_write():
    work()
