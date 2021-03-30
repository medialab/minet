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
