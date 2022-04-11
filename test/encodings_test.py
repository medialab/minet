# =============================================================================
# Minet Encodings Unit Tests
# =============================================================================
from minet.encodings import is_supported_encoding

SUPPORT_TESTS = [
    ("utf8", True),
    ("L1", True),
    ("UTF-8", True),
    ("uTf 8", True),
    ("utf-8859-1", False),
]


class TestEncodings(object):
    def test_is_supported_encoding(self):
        for value, result in SUPPORT_TESTS:
            assert is_supported_encoding(value) == result
