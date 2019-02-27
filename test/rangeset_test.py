# =============================================================================
# Minet RangeSet Unit Tests
# =============================================================================
from minet.range_set import RangeSet


class TestRangeSet(object):
    def test_basics(self):
        s = RangeSet()

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
