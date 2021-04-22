# =============================================================================
# Minet Fetch Unit Tests
# =============================================================================
from minet.web import request
from minet.exceptions import InvalidURLError


class TestFetch(object):
    def test_bad_protocol(self):
        err, _ = request('ttps://lemonde.fr')

        assert type(err) is InvalidURLError
