# =============================================================================
# Minet FileSystem Utilities
# =============================================================================
#
# Multiple helper functions related to reading and writing files.
#
import os
import gzip
import codecs
from threading import Lock
from os.path import basename, join
from ural import get_hostname, get_normalized_hostname


def read_potentially_gzipped_path(path, encoding='utf-8'):
    if path.endswith('.gz'):
        with open(path, 'rb') as f:
            raw_bytes = gzip.decompress(f.read())

        raw = raw_bytes.decode(encoding, errors='replace')
    else:
        with codecs.open(path, 'r', encoding=encoding, errors='replace') as f:
            raw = f.read()

    return raw


MAKEDIRS_LOCK = Lock()


def threadsafe_makedirs(path):
    with MAKEDIRS_LOCK:
        os.makedirs(path, exist_ok=True)


class FolderStrategy(object):
    def apply(self):
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
                return None

            if length <= 0:
                return None

            return PrefixFolderStrategy(length)

        raise None


class FlatFolderStrategy(FolderStrategy):
    def apply(self, filename, **kwargs):
        return filename


class PrefixFolderStrategy(FolderStrategy):
    def __init__(self, length):
        self.length = length

    def apply(self, filename, **kwargs):
        base = basename(filename).split('.', 1)[0]

        return join(base[:self.length], filename)


class HostnameFolderStrategy(FolderStrategy):
    def apply(self, filename, url, **kwargs):
        hostname = get_hostname(url)

        if not hostname:
            hostname = 'unknown-host'

        return join(hostname, filename)


class NormalizedHostnameFolderStrategy(FolderStrategy):
    def apply(self, filename, url, **kwargs):
        hostname = get_normalized_hostname(
            url,
            normalize_amp=False,
            strip_lang_subdomains=True,
            infer_redirection=False
        )

        if not hostname:
            hostname = 'unknown-host'

        return join(hostname, filename)
