# =============================================================================
# Minet Utils Unit Tests
# =============================================================================
from minet.utils import (
    fix_ensure_ascii_json_string,
    PseudoFStringFormatter,
    is_binary_mimetype,
    message_flatmap,
)

MIMETYPES = [("text/html", False), ("application/json", False), ("image/png", True)]


class TestUtils(object):
    def test_fix_ensure_ascii_json_string(self):
        assert (
            fix_ensure_ascii_json_string("Marie-H\\u00e9l\\u00e8ne") == "Marie-Hélène"
        )

    def test_pseudo_fstring_formatter(self):
        formatter = PseudoFStringFormatter()

        result = formatter.format('{line["test"]}', line={"test": "hello"})

        assert result == "hello"

    def test_is_binary_mimetype(self):
        for mimetype, result in MIMETYPES:
            assert is_binary_mimetype(mimetype) is result

    def test_message_flatmap(self):
        assert message_flatmap("test") == "test"
        assert message_flatmap("test1", "test2") == "test1 test2"
        assert message_flatmap(["test1", "test2"]) == "test1\ntest2"
        assert (
            message_flatmap("test1", ["test2", "test3"], "test4")
            == "test1 test2\ntest3 test4"
        )
