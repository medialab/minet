# =============================================================================
# Minet CLI Utils Unit Tests
# =============================================================================
from minet.cli.utils import CsvIO


class TestCLIUtils(object):
    def test_csv_io(self):
        assert CsvIO('name', 'Yomgui').getvalue().strip() == 'name\nYomgui'
        assert CsvIO('name', 'Yomgui, the real').getvalue().strip() == 'name\n"Yomgui, the real"'
