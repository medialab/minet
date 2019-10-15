# =============================================================================
# Minet Fetch Unit Tests
# =============================================================================
import pytest
from minet.utils import create_safe_pool, request
from minet.exceptions import InvalidURLError


class TestFetch(object):

    def test_bad_protocol(self):
        http = create_safe_pool()
        err, _ = request(http, 'ttps://lemonde.fr')

        assert type(err) is InvalidURLError
