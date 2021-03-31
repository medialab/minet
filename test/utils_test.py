# =============================================================================
# Minet Utils Unit Tests
# =============================================================================
import pytest

from minet.utils import (
    fix_ensure_ascii_json_string,
    nested_get,
    namedrecord,
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

    def test_namedrecord(self):
        Record = namedrecord('Record', ['x', 'y'])

        r = Record(x=34, y=22)

        assert len(r) == 2
        assert list(r) == [34, 22]
        assert r[0] == 34
        assert r.x == 34
        assert r['x'] == 34

        with pytest.raises(KeyError):
            r['z']

        assert r.get('x') == 34
        assert r.get(0) == 34
        assert r.get(54) is None
        assert r.get('z') is None

        Video = namedrecord(
            'Video',
            ['title', 'has_captions', 'tags'],
            boolean=['has_captions'],
            plural=['tags']
        )

        v = Video('Super video', True, ['film', 'pop'])

        assert v.as_csv_row() == ['Super video', 'true', 'film|pop']
        assert v.as_dict() == {
            'title': 'Super video',
            'has_captions': True,
            'tags': ['film', 'pop']
        }
