# =============================================================================
# Minet Multiprocessing Utilities
# =============================================================================
#
# Multiple helper functions related to multiprocessing execution.
#
import sys
import multiprocessing


def half_cpus(override=None):
    """
    Function returning roughly half of the available CPUs.
    """
    count = multiprocessing.cpu_count() if override is None else override
    half = count // 2

    if count <= 2:
        return 1

    if half % 2 != 0:
        half += 1

    return half


# NOTE: this is a class and not a decorator so it can be pickled
class WorkerWrapper(object):
    __slots__ = ("fn",)

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        try:
            return self.fn(*args, **kwargs)
        except KeyboardInterrupt:
            sys.exit(1)


class LazyPool(object):
    """
    A multiprocessing.Pool shim that won't start subprocesses if the desired
    number of workers is only one.
    """

    def __init__(self, processes=None, initializer=None, initargs=None):
        if processes is None:
            processes = half_cpus()

        self.processes = processes

        self.actually_multiprocessed = processes > 1
        self.inner_pool = None

        if self.actually_multiprocessed:
            self.inner_pool = multiprocessing.Pool(
                processes, initializer=initializer, initargs=initargs or tuple()
            )
        else:
            if initializer is not None:
                initializer(*initargs)

    def imap(self, worker, tasks, chunksize: int = 1, unordered: bool = False):
        if self.actually_multiprocessed:
            assert self.inner_pool is not None

            fn = self.inner_pool.imap_unordered if unordered else self.inner_pool.imap

            yield from fn(WorkerWrapper(worker), tasks, chunksize=chunksize)
        else:
            for task in tasks:
                yield worker(task)

    def imap_unordered(self, worker, tasks, chunksize: int = 1):
        return self.imap(worker, tasks, chunksize=chunksize, unordered=False)

    def __enter__(self):
        if self.actually_multiprocessed:
            assert self.inner_pool is not None

            self.inner_pool.__enter__()

        return self

    def __exit__(self, *args):
        if self.actually_multiprocessed:
            assert self.inner_pool is not None

            self.inner_pool.__exit__(*args)
