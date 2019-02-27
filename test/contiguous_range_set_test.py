# =============================================================================
# Minet ContiguousRangeSet Unit Tests
# =============================================================================
from minet.contiguous_range_set import ContiguousRangeSet


class TestContiguousRangeSet(object):
    def test_basics(self):
        s = ContiguousRangeSet()

        s.add(3)

        assert s.intervals == [(3, 3)]

        s.add(7)

        assert s.intervals == [(3, 3), (7, 7)]

        s.add(1)

        assert s.intervals == [(1, 1), (3, 3), (7, 7)]

        s.add(2)

        assert s.intervals == [(1, 3), (7, 7)]

        s.add(4)

        assert s.intervals == [(1, 4), (7, 7)]

        s.add(6)

        assert s.intervals == [(1, 4), (6, 7)]

        s.add(5)

        assert s.intervals == [(1, 7)]

        s.add(-1)

        assert s.intervals == [(-1, -1), (1, 7)]

    def test_contains(self):
        s = ContiguousRangeSet()

        s.add(1)
        s.add(2)
        s.add(4)
        s.add(5)

        assert 1 in s
        assert 2 in s
        assert 3 not in s
        assert 4 in s
        assert 5 in s
        assert 6 not in s
        assert 7 not in s
        assert 100 not in s
        assert -1 not in s
