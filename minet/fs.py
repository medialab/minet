# =============================================================================
# Minet FileSystem Utilities
# =============================================================================
#
# Multiple helper functions related to reading and writing files.
#
import gzip
from os import makedirs
from os.path import basename, join, splitext, abspath, normpath, dirname
from ural import get_hostname, get_normalized_hostname
from quenouille import NamedLocks

from minet.exceptions import FilenameFormattingError
from minet.utils import md5, PseudoFStringFormatter


def read_potentially_gzipped_path(path, encoding="utf-8"):
    open_fn = open
    flag = "r"

    if path.endswith(".gz"):
        open_fn = gzip.open
        flag = "rt"

    with open_fn(path, flag, encoding=encoding, errors="replace") as f:
        return f.read()


class FolderStrategy(object):
    def __call__(self):
        raise NotImplementedError

    @staticmethod
    def from_name(name):
        if name == "flat":
            return FlatFolderStrategy()

        if name == "hostname":
            return HostnameFolderStrategy()

        if name == "normalized-hostname":
            return NormalizedHostnameFolderStrategy()

        if name.startswith("prefix-"):
            length = name.split("prefix-")[-1]

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
        base = basename(filename).split(".", 1)[0]

        return join(base[: self.length], filename)


class HostnameFolderStrategy(FolderStrategy):
    def __call__(self, filename, url, **kwargs):
        hostname = get_hostname(url)

        if not hostname:
            hostname = "unknown-host"

        return join(hostname, filename)


class NormalizedHostnameFolderStrategy(FolderStrategy):
    def __call__(self, filename, url, **kwargs):
        hostname = get_normalized_hostname(
            url,
            normalize_amp=False,
            strip_lang_subdomains=True,
            infer_redirection=False,
        )

        if not hostname:
            hostname = "unknown-host"

        return join(hostname, filename)


class FilenameBuilder(object):
    def __init__(self, folder_strategy=None, template=None):
        self.folder_strategy = None

        if folder_strategy is not None:
            self.folder_strategy = FolderStrategy.from_name(folder_strategy)

        self.formatter = PseudoFStringFormatter()
        self.template = template

    def __call__(
        self, url=None, filename=None, ext=None, formatter_kwargs={}, compressed=False
    ):
        original_ext = None

        if filename is None:
            base = md5(url)
        else:
            base, original_ext = splitext(filename)

        # We favor the extension found in given filename, else we fallback
        # on the provided one if any (usually inferred from http response)
        ext = original_ext if original_ext else (ext or "")

        if self.template is not None:
            try:
                filename = self.formatter.format(
                    self.template, value=base, ext=ext, **formatter_kwargs
                )
            except Exception as e:
                raise FilenameFormattingError(reason=e, template=self.template)
        else:
            filename = base + ext

        if self.folder_strategy:
            filename = self.folder_strategy(filename, url=url)

        if compressed:
            filename += ".gz"

        return filename


class ThreadSafeFilesWriter(object):
    def __init__(self, root_directory=""):
        self.root_directory = root_directory
        self.folder_locks = NamedLocks()
        self.file_locks = NamedLocks()

    def resolve(self, filename, relative=False):
        full_path = join(self.root_directory, filename)

        if relative:
            return normpath(full_path)

        return abspath(full_path)

    def makedirs(self, directory):
        if not directory:
            return

        # TODO: cache
        with self.folder_locks[directory]:
            makedirs(directory, exist_ok=True)

    def write(self, filename, contents, binary=True, compress=False):
        if binary and not isinstance(contents, bytes):
            raise TypeError("contents must be bytes if binary=True")

        if not binary and not isinstance(contents, str):
            raise TypeError("contents must be str if binary=False")

        if compress and not binary:
            raise NotImplementedError

        filename = self.resolve(filename)
        directory = dirname(filename)

        # NOTE: Could have prefix-free locking as a bonus...
        self.makedirs(directory)

        open_kwargs = {"mode": "wb" if binary else "w"}

        if not binary:
            open_kwargs["encoding"] = "utf-8"

        if compress:
            open_fn = gzip.open
        else:
            open_fn = open

        with self.file_locks[filename]:
            with open_fn(filename, **open_kwargs) as f:
                f.write(contents)
