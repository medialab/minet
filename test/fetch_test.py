# =============================================================================
# Minet Fetch Unit Tests
# =============================================================================
from pytest import raises

from minet.web import request
from minet.exceptions import InvalidURLError


class TestFetch(object):
    def test_bad_protocol(self):
        with raises(InvalidURLError):
            request("ttps://lemonde.fr")
