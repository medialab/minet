# =============================================================================
# Minet FS Unit Tests
# =============================================================================
import os
import pytest

from minet.fs import (
    FolderStrategy,
    FlatFolderStrategy,
    PrefixFolderStrategy,
    HostnameFolderStrategy,
    NormalizedHostnameFolderStrategy
)


class TestFS(object):
    def test_folder_strategy(self):

        # Don't test on windows yet
        if os.sep != '/':
            return

        flat = FolderStrategy.from_name('flat')

        assert isinstance(flat, FlatFolderStrategy)

        assert flat.apply(filename='test/ok/whatever.html') == 'test/ok/whatever.html'

        prefix = FolderStrategy.from_name('prefix-5')

        assert isinstance(prefix, PrefixFolderStrategy)

        assert prefix.apply(filename='test/ok/whatever.html') == 'whate/test/ok/whatever.html'

        hostname = FolderStrategy.from_name('hostname')

        assert hostname.apply(filename='test.html', url='https://www.lemonde.fr/test.html') == 'www.lemonde.fr/test.html'

        normalized_hostname = FolderStrategy.from_name('normalized-hostname')

        assert normalized_hostname.apply(filename='test.html', url='https://www.lemonde.fr/test.html') == 'lemonde.fr/test.html'
