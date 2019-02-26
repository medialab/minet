# =============================================================================
# Minet RangeSet Unit Tests
# =============================================================================
from minet.range_set import RangeSet


class TestRangeSet(object):
    def test_basics(self):
        s = RangeSet()

        s.add(3)

        assert s.intervals == [(3, 3)]
        assert s.min == (3, 3)
        assert s.max == (3, 3)

        s.add(7)

        assert s.intervals == [(3, 7)]
        assert s.min == (3, 7)
        assert s.max == (3, 7)

        print(s.min, s.max, s.intervals)
