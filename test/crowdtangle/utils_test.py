# =============================================================================
# Minet Crowdtangle Utils Unit Tests
# =============================================================================
from minet.crowdtangle.utils import (
    get_last_day_of_month,
    complement_date
)

LAST_DAY = [
    ('2020', '12', '31'),
    ('2020', '04', '30'),
    ('2020', '02', '29'),
    ('2019', '02', '28')
]

COMPLEMENT = [
    ('2020', 'start', '2020-01-01T00:00:00'),
    ('2020-04', 'start', '2020-04-01T00:00:00'),
    ('2020-04-03', 'start', '2020-04-03T00:00:00'),
    ('2020-04-03T21:34:35', 'start', '2020-04-03T21:34:35'),
    ('2020', 'end', '2020-12-31T23:59:59'),
    ('2020-04', 'end', '2020-04-30T23:59:59'),
    ('2020-04-03', 'end', '2020-04-03T23:59:59'),
    ('2020-04-03T21:34:35', 'end', '2020-04-03T21:34:35')
]


class TestCrowdtangleUtils(object):
    def test_get_last_day_of_month(self):
        for year, month, last_day in LAST_DAY:
            assert get_last_day_of_month(year, month) == last_day

    def test_complement_date(self):
        for d, bound, complete in COMPLEMENT:
            assert complement_date(d, bound) == complete, d
