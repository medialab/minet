# =============================================================================
# Minet Multiprocessing Unit Tests
# =============================================================================
from minet.multiprocessing import half_cpus


class TestMultiprocessing(object):
    def test_half_cpus(self):
        assert half_cpus(8) == 4
        assert half_cpus(7) == 4
        assert half_cpus(4) == 2
        assert half_cpus(3) == 2
        assert half_cpus(2) == 1
        assert half_cpus(1) == 1
