# =============================================================================
# =============================================================================
# Minet Dates Unit Tests
# =============================================================================
import pytest
from datetime import datetime

from minet.dates import datetime_from_partial_iso_format


class TestDates(object):
    def test_datetime_from_partial_iso_format(self):
        assert datetime_from_partial_iso_format("2008") == datetime(2008, 1, 1)
        assert datetime_from_partial_iso_format("2008-02") == datetime(2008, 2, 1)
        assert datetime_from_partial_iso_format("2008-02-21") == datetime(2008, 2, 21)
        assert datetime_from_partial_iso_format("2008-02-21T12") == datetime(
            2008, 2, 21, 12
        )
        assert datetime_from_partial_iso_format("2008-02-21T12:45") == datetime(
            2008, 2, 21, 12, 45
        )
        assert datetime_from_partial_iso_format("2008-02-21T12:45:46") == datetime(
            2008, 2, 21, 12, 45, 46
        )
        assert datetime_from_partial_iso_format("2008-02-21T12:45:46Z") == datetime(
            2008, 2, 21, 12, 45, 46
        )
        assert datetime_from_partial_iso_format(
            "2008-02-21T12:45:46.123456"
        ) == datetime(2008, 2, 21, 12, 45, 46, 123456)
        assert datetime_from_partial_iso_format(
            "2008-02-21T12:45:46.123456Z"
        ) == datetime(2008, 2, 21, 12, 45, 46, 123456)

        with pytest.raises(ValueError):
            datetime_from_partial_iso_format("2008-02-30")

        assert datetime_from_partial_iso_format("2008", upper_bound=True) == datetime(
            2008, 12, 31, 23, 59, 59, 999999
        )
        assert datetime_from_partial_iso_format(
            "2008-02", upper_bound=True
        ) == datetime(2008, 2, 29, 23, 59, 59, 999999)
        assert datetime_from_partial_iso_format(
            "2008-02-21", upper_bound=True
        ) == datetime(2008, 2, 21, 23, 59, 59, 999999)
        assert datetime_from_partial_iso_format(
            "2008-02-21T12", upper_bound=True
        ) == datetime(2008, 2, 21, 12, 59, 59, 999999)
        assert datetime_from_partial_iso_format(
            "2008-02-21T12:45", upper_bound=True
        ) == datetime(2008, 2, 21, 12, 45, 59, 999999)
        assert datetime_from_partial_iso_format(
            "2008-02-21T12:45:46", upper_bound=True
        ) == datetime(2008, 2, 21, 12, 45, 46, 999999)
        assert datetime_from_partial_iso_format(
            "2008-02-21T12:45:46Z", upper_bound=True
        ) == datetime(2008, 2, 21, 12, 45, 46, 999999)
