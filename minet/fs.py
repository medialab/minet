# =============================================================================
# Minet FileSystem Utilities
# =============================================================================
#
# Multiple helper functions related to reading and writing files.
#
from typing import Union, Optional, cast, Dict

import os
import gzip
import json
import yaml
from ebbe.decorators import with_defer
from os import makedirs, PathLike
from os.path import basename, join, splitext, abspath, normpath, dirname
from ural import (
    get_hostname,
    get_normalized_hostname,
    get_fingerprinted_hostname,
    safe_urlsplit,
    pathsplit,
)
from quenouille import NamedLocks

from minet.exceptions import (
    FilenameFormattingError,
    DefinitionInvalidFormatError,
    CouldNotInferEncodingError,
)
from minet.utils import md5, PseudoFStringFormatter
from minet.encodings import infer_encoding
from minet.sqlar import SQLiteArchive


def read_potentially_gzipped_path(
    path,
    encoding: Optional[str] = None,
    errors: str = "replace",
    fallback_encoding: Optional[str] = None,
) -> str:
    open_fn = open
    flag = "r" if encoding is not None else "rb"

    if path.endswith(".gz"):
        open_fn = gzip.open
        flag = "rt" if encoding is not None else "r"

    if encoding is None:
        with open_fn(path, flag) as f:
            binary = f.read()
            encoding = infer_encoding(binary)

            if encoding is None:
                if fallback_encoding is not None:
                    encoding = fallback_encoding
                else:
                    raise CouldNotInferEncodingError

            return binary.decode(encoding, errors=errors)

    with open_fn(path, flag, encoding=encoding, errors=errors) as f:
        return f.read()


@with_defer()
def load_definition(f, *, defer=None, encoding: str = "utf-8") -> Dict:
    if isinstance(f, (str, PathLike)):
        path = str(f)
        f = open(path, encoding=encoding)
        defer(f.close)  # type: ignore
    else:
        path = f.name

    if path.endswith(".json"):
        definition = json.load(f)

    elif path.endswith(".yml") or path.endswith(".yaml"):
        definition = yaml.safe_load(f)

    else:
        raise DefinitionInvalidFormatError

    return definition


class FolderStrategy(object):
    CHOICES = ["flat", "fullpath", "hostname", "normalize-hostname", "prefix-x"]

    DOCUMENTATION = """
        . "flat": default choice, all files will be written in the indicated
            content folder.

        . "fullpath": all files will be written in a folder consisting of the
            url hostname and then its path.

        . "prefix-x": e.g. "prefix-4", files will be written in folders
            having a name that is the first x characters of the file's name.
            This is an efficient way to partition content into folders containing
            roughly the same number of files if the file names are random (which
            is the case by default since md5 hashes will be used).

        . "hostname": files will be written in folders based on their url's
            full host name.

        . "normalized-hostname": files will be written in folders based on
            their url's hostname stripped of some undesirable parts (such as
            "www.", or "m.", for instance).

        . "fingerprinted-hostname": files will be written in folders based on
            their url's hostname stripped of some more undesirable parts (such as
            "fr.", for instance) and their public suffix will be dropped.
    """

    def __call__(self):
        raise NotImplementedError

    @staticmethod
    def from_name(name):
        if name == "flat":
            return FlatFolderStrategy()

        if name == "fullpath":
            return FullPathFolderStrategy()

        if name == "hostname":
            return HostnameFolderStrategy()

        if name == "normalized-hostname":
            return NormalizedHostnameFolderStrategy()

        if name == "fingerprinted-hostname":
            return FingerprintedHostnameFolderStrategy()

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


class FullPathFolderStrategy(FolderStrategy):
    def __call__(self, filename, url, **kwargs):
        parsed = safe_urlsplit(url)
        final_path = [cast(str, parsed.hostname)]

        path = pathsplit(parsed.path)

        if path and "." in path[-1]:
            path.pop()

        final_path += path

        # NOTE: dealing with typical max filename length
        for i in range(len(final_path)):
            item = final_path[i]

            if len(item) > 255:
                final_path[i] = item[:255]

        return join(os.sep.join(final_path), filename)


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
            infer_redirection=False,
        )

        if not hostname:
            hostname = "unknown-host"

        return join(hostname, filename)


class FingerprintedHostnameFolderStrategy(FolderStrategy):
    def __call__(self, filename, url, **kwargs):
        hostname = get_fingerprinted_hostname(url, strip_suffix=True)

        if not hostname:
            hostname = "unknown-host"

        return join(hostname, filename)


class FilenameBuilder(object):
    folder_strategy: Optional[FolderStrategy]

    def __init__(
        self,
        folder_strategy: Optional[Union[str, FolderStrategy]] = None,
        template=None,
    ):
        self.folder_strategy = None

        if folder_strategy is not None and isinstance(folder_strategy, str):
            self.folder_strategy = FolderStrategy.from_name(folder_strategy)
        elif isinstance(folder_strategy, FolderStrategy):
            self.folder_strategy = folder_strategy

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

        # Extension normalization
        if ext:
            ext = "." + ext.lstrip(".")

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


class ThreadSafeFileWriter(object):
    def __init__(self, root_directory: Optional[str] = None, sqlar: bool = False):
        self.root_directory = root_directory or ""
        self.folder_locks = NamedLocks()
        self.file_locks = NamedLocks()
        self.sqlar = sqlar
        self.archive = None

        if self.sqlar:
            self.root_directory += ".sqlar"
            self.archive = SQLiteArchive(self.root_directory)

    def resolve(self, filename: str, relative: bool = False, compress: bool = False):
        full_path = join(self.root_directory, filename)

        if compress and not full_path.endswith(".gz"):
            full_path += ".gz"

        if relative:
            return normpath(full_path)

        return normpath(abspath(full_path))

    def makedirs(self, directory: str) -> None:
        if not directory:
            return

        # TODO: cache
        with self.folder_locks[directory]:
            makedirs(directory, exist_ok=True)

    def write(
        self,
        filename: str,
        contents: Union[str, bytes],
        compress: bool = False,
        relative: bool = False,
    ) -> str:
        if self.sqlar:
            assert self.archive is not None

            if not isinstance(contents, bytes):
                contents = contents.encode("utf-8")

            self.archive.write(filename, contents)

            return filename

        binary = isinstance(contents, bytes)
        filename = self.resolve(filename, relative=relative, compress=compress)
        directory = dirname(filename)

        # NOTE: Could have prefix-free locking as a bonus...
        self.makedirs(directory)

        open_kwargs = {"mode": "wb" if binary else "w"}

        if not binary:
            open_kwargs["encoding"] = "utf-8"

        if compress:
            open_fn = gzip.open

            if not binary:
                open_kwargs["mode"] = "wt"
        else:
            open_fn = open

        with self.file_locks[filename]:
            with open_fn(filename, **open_kwargs) as f:
                f.write(contents)  # type: ignore

        return filename
