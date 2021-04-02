# =============================================================================
# Minet Utils Unit Tests
# =============================================================================
import pytest

from minet.utils import (
    fix_ensure_ascii_json_string,
    nested_get,
    PseudoFStringFormatter
)

NESTED_OBJECT = {
    'a': {
        'b': [{'c': 4}],
        'd': {
            'e': 5
        }
    }
}


class TestUtils(object):
    def test_nested_get(self):
        assert nested_get('a.d.e', NESTED_OBJECT) == 5
        assert nested_get('b.d.a.a', NESTED_OBJECT) is None
        assert nested_get(['a', 'b', 0, 'c'], NESTED_OBJECT) == 4
        assert nested_get(['a', 'b', 1, 'c', 2], NESTED_OBJECT) is None

    def test_fix_ensure_ascii_json_string(self):
        assert fix_ensure_ascii_json_string('Marie-H\\u00e9l\\u00e8ne') == 'Marie-Hélène'

    def test_pseudo_fstring_formatter(self):
        formatter = PseudoFStringFormatter()

        result = formatter.format('{line["test"]}', line={'test': 'hello'})

        assert result == 'hello'
