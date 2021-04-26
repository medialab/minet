# =============================================================================
# Minet FS Unit Tests
# =============================================================================
import os
import pytest
from casanova import DictLikeRow

from minet.fs import (
    FolderStrategy,
    FlatFolderStrategy,
    PrefixFolderStrategy,
    HostnameFolderStrategy,
    NormalizedHostnameFolderStrategy,
    FilenameBuilder
)
from minet.exceptions import FilenameFormattingError


class TestFS(object):
    def test_folder_strategy(self):

        # Don't test on windows yet
        if os.sep != '/':
            return

        flat = FolderStrategy.from_name('flat')

        assert isinstance(flat, FlatFolderStrategy)

        assert flat(filename='test/ok/whatever.html') == 'test/ok/whatever.html'

        prefix = FolderStrategy.from_name('prefix-5')

        assert isinstance(prefix, PrefixFolderStrategy)

        assert prefix(filename='test/ok/whatever.html') == 'whate/test/ok/whatever.html'
        assert prefix(filename='a.html') == 'a/a.html'

        hostname = FolderStrategy.from_name('hostname')

        assert isinstance(hostname, HostnameFolderStrategy)

        assert hostname(filename='test.html', url='https://www.lemonde.fr/test.html') == 'www.lemonde.fr/test.html'

        normalized_hostname = FolderStrategy.from_name('normalized-hostname')

        assert isinstance(normalized_hostname, NormalizedHostnameFolderStrategy)

        assert normalized_hostname(filename='test.html', url='https://www.lemonde.fr/test.html') == 'lemonde.fr/test.html'

    def test_filename_builder(self):
        builder = FilenameBuilder()

        assert builder('https://www.lemonde.fr') == 'f8bceab28da05bf9ed8678be4690bf64'
        assert builder('https://www.lemonde.fr', ext='.html') == 'f8bceab28da05bf9ed8678be4690bf64.html'
        assert builder('https://www.lemonde.fr', filename='lemonde', ext='.html') == 'lemonde.html'
        assert builder('https://www.lemonde.fr', filename='lemonde.txt') == 'lemonde.txt'
        assert builder('https://www.lemonde.fr', filename='lemonde.txt', ext='.html') == 'lemonde.txt'
        assert builder('https://www.lemonde.fr', filename='folder/lemonde.txt', ext='.html') == 'folder/lemonde.txt'

        builder = FilenameBuilder(template='prefix-{value}{ext}.bak')

        assert builder('https://www.lemonde.fr') == 'prefix-f8bceab28da05bf9ed8678be4690bf64.bak'
        assert builder('https://www.lemonde.fr', ext='.html') == 'prefix-f8bceab28da05bf9ed8678be4690bf64.html.bak'
        assert builder('https://www.lemonde.fr', filename='lemonde', ext='.html') == 'prefix-lemonde.html.bak'
        assert builder('https://www.lemonde.fr', filename='lemonde.txt') == 'prefix-lemonde.txt.bak'
        assert builder('https://www.lemonde.fr', filename='lemonde.txt', ext='.html') == 'prefix-lemonde.txt.bak'
        assert builder('https://www.lemonde.fr', filename='folder/lemonde.txt', ext='.html') == 'prefix-folder/lemonde.txt.bak'

        builder = FilenameBuilder(template='{line.name}{ext}')
        row = DictLikeRow({'name': 0}, ['lefigaro'])

        with pytest.raises(FilenameFormattingError):
            builder('https://www.lefigaro.fr')

        assert builder('https://www.lefigaro.fr', formatter_kwargs={'line': row}) == 'lefigaro'
        assert builder('https://www.lefigaro.fr', formatter_kwargs={'line': row}, ext='.html') == 'lefigaro.html'
        assert builder('https://www.lefigaro.fr', filename='nothing', formatter_kwargs={'line': row}) == 'lefigaro'
        assert builder('https://www.lefigaro.fr', filename='nothing.bak', formatter_kwargs={'line': row}) == 'lefigaro.bak'

        builder = FilenameBuilder(folder_strategy='prefix-4')

        assert builder('https://www.liberation.fr') == '9bd3/9bd303edd0b0aaa5b210d0ddf63779ef'
        assert builder('https://www.liberation.fr', filename='liberation.html') == 'libe/liberation.html'
