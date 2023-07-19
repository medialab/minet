# =============================================================================
# Minet Headers Utils Unit Tests
# =============================================================================
from minet.headers import parse_http_refresh

HTTP_REFRESH_TESTS = [
    (
        "0;url=https://www.youtube.com/watch?v=sTJ1XwGDcA4",
        (0, "https://www.youtube.com/watch?v=sTJ1XwGDcA4"),
    ),
    (
        "0;url=https://www.youtube.com/watch?v=sTJ1XwGDcA4   ",
        (0, "https://www.youtube.com/watch?v=sTJ1XwGDcA4"),
    ),
    (
        "   0;URL=https://www.youtube.com/watch?v=sTJ1XwGDcA4",
        (0, "https://www.youtube.com/watch?v=sTJ1XwGDcA4"),
    ),
    ("test;url=https://www.youtube.com/watch?v=sTJ1XwGDcA4", None),
    ("0;/www.youtube.com/watch?v=sTJ1XwGDcA4", None),
]


class TestHeaders(object):
    def test_parse_http_refresh(self):
        for header_value, result in HTTP_REFRESH_TESTS:
            assert parse_http_refresh(header_value) == result
