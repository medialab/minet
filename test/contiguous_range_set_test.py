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

    def test_stateful_contains(self):
        s = ContiguousRangeSet()

        s.add(0)
        s.add(1)
        s.add(2)
        s.add(5)
        s.add(7)
        s.add(6)

        assert s.intervals == [(0, 2), (5, 7)]

        assert s.stateful_contains(0)
        assert s.stateful_contains(1)
        assert s.stateful_contains(2)
        assert not s.stateful_contains(3)
        assert not s.stateful_contains(4)
        assert s.stateful_contains(5)
        assert s.stateful_contains(6)
        assert s.stateful_contains(7)
        assert not s.stateful_contains(8)
        assert not s.stateful_contains(1)
        assert not s.stateful_contains(3)
        assert not s.stateful_contains(6)
        assert not s.stateful_contains(-1)
        assert not s.stateful_contains(100)
