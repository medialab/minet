# =============================================================================
# Minet Multiprocessing Utilities
# =============================================================================
#
# Multiple helper functions related to multiprocessing execution.
#
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
                processes,
                initializer=initializer,
                initargs=initargs
            )
        else:
            if initializer is not None:
                initializer(*initargs)

    def imap_unordered(self, worker, tasks):
        if self.actually_multiprocessed:
            yield from self.inner_pool.imap_unordered(worker, tasks)
        else:
            for task in tasks:
                yield worker(task)

    def __enter__(self):
        if self.actually_multiprocessed:
            self.inner_pool.__enter__()

        return self

    def __exit__(self, *args):
        if self.actually_multiprocessed:
            self.inner_pool.__exit__(*args)
