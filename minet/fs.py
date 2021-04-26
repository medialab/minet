# =============================================================================
# Minet FileSystem Utilities
# =============================================================================
#
# Multiple helper functions related to reading and writing files.
#
import gzip
import codecs
from os.path import basename, join, splitext
from ural import get_hostname, get_normalized_hostname
from functools import partial

from minet.exceptions import FilenameFormattingError
from minet.utils import md5, PseudoFStringFormatter


def read_potentially_gzipped_path(path, encoding='utf-8'):
    if path.endswith('.gz'):
        with open(path, 'rb') as f:
            raw_bytes = gzip.decompress(f.read())

        raw = raw_bytes.decode(encoding, errors='replace')
    else:
        with codecs.open(path, 'r', encoding=encoding, errors='replace') as f:
            raw = f.read()

    return raw


class FolderStrategy(object):
    def __call__(self):
        raise NotImplementedError

    @staticmethod
    def from_name(name):
        if name == 'flat':
            return FlatFolderStrategy()

        if name == 'hostname':
            return HostnameFolderStrategy()

        if name == 'normalized-hostname':
            return NormalizedHostnameFolderStrategy()

        if name.startswith('prefix-'):
            length = name.split('prefix-')[-1]

            try:
                length = int(length)
            except ValueError:
                raise TypeError

            if length <= 0:
                raise TypeError

            return PrefixFolderStrategy(length)

        raise TypeError


class FlatFolderStrategy(FolderStrategy):
    def __call__(self, filename, **kwargs):
        return filename


class PrefixFolderStrategy(FolderStrategy):
    def __init__(self, length):
        self.length = length

    def __call__(self, filename, **kwargs):
        base = basename(filename).split('.', 1)[0]

        return join(base[:self.length], filename)


class HostnameFolderStrategy(FolderStrategy):
    def __call__(self, filename, url, **kwargs):
        hostname = get_hostname(url)

        if not hostname:
            hostname = 'unknown-host'

        return join(hostname, filename)


class NormalizedHostnameFolderStrategy(FolderStrategy):
    def __call__(self, filename, url, **kwargs):
        hostname = get_normalized_hostname(
            url,
            normalize_amp=False,
            strip_lang_subdomains=True,
            infer_redirection=False
        )

        if not hostname:
            hostname = 'unknown-host'

        return join(hostname, filename)


class FilenameBuilder(object):
    def __init__(self, folder_strategy=None, template=None):
        self.folder_strategy = None

        if folder_strategy is not None:
            self.folder_strategy = FolderStrategy.from_name(folder_strategy)

        self.formatter = PseudoFStringFormatter()
        self.template = None

        if template is not None:
            self.template = partial(self.formatter.format, template)

    def __call__(self, url=None, filename=None, ext=None, formatter_kwargs={}):
        original_ext = None

        if filename is None:
            base = md5(url)
        else:
            base, original_ext = splitext(filename)

        # We favor the extension found in given filename, else we fallback
        # on the provided one if any (usually inferred from http response)
        ext = original_ext if original_ext else (ext or '')

        if self.template is not None:
            try:
                filename = self.template(
                    value=base,
                    ext=ext,
                    **formatter_kwargs
                )
            except Exception:
                raise FilenameFormattingError
        else:
            filename = base + ext

        if self.folder_strategy:
            filename = self.folder_strategy(filename)

        return filename
