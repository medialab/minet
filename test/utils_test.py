# =============================================================================
# Minet Utils Unit Tests
# =============================================================================
from minet.utils import (
    fix_ensure_ascii_json_string,
    PseudoFStringFormatter,
    is_binary_mimetype
)

MIMETYPES = [
    ('text/html', False),
    ('application/json', False),
    ('image/png', True)
]


class TestUtils(object):
    def test_fix_ensure_ascii_json_string(self):
        assert fix_ensure_ascii_json_string('Marie-H\\u00e9l\\u00e8ne') == 'Marie-Hélène'

    def test_pseudo_fstring_formatter(self):
        formatter = PseudoFStringFormatter()

        result = formatter.format('{line["test"]}', line={'test': 'hello'})

        assert result == 'hello'

    def test_is_binary_mimetype(self):
        for mimetype, result in MIMETYPES:
            assert is_binary_mimetype(mimetype) is result
