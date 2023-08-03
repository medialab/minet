from typing import Optional, Iterator

import sqlite3
import zlib
from os import stat
from os.path import isfile
from threading import Lock
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from minet.exceptions import SQLArchiveInvalidError
from minet.utils import iterate_over_sqlite_cursor

# Extraction using the sqlite3 command line:
#   $ sqlite3 -Axvf archive.sqlar
#   $ sqlite3 archive.sqlar ".ar -xv --directory archive"

# References:
#  - https://www.sqlite.org/sqlar/doc/trunk/README.md
#  - https://www.sqlite.org/sqlar.html
#  - https://www.sqlite.org/intern-v-extern-blob.html
#  - https://www.sqlite.org/fasterthanfs.html
#  - https://docs.rs/sqlar/latest/sqlar/
#  - https://github.com/Frojdholm/pysqlar

# NOTE: taken from pysqlar:
SQLAR_TABLE_EXPECTED_RESULT = [
    (0, "name", "TEXT", 0, None, 1),
    (1, "mode", "INT", 0, None, 0),
    (2, "mtime", "INT", 0, None, 0),
    (3, "sz", "INT", 0, None, 0),
    (4, "data", "BLOB", 0, None, 0),
]

SQL_PRAGMAS = """
PRAGMA journal_mode=wal;
PRAGMA synchronous=normal;
PRAGMA page_size=16384;
"""

SQL_CREATE = """
CREATE TABLE sqlar (
  name TEXT PRIMARY KEY,  -- name of the file
  mode INT,               -- access permissions
  mtime INT,              -- last modification time
  sz INT,                 -- original file size
  data BLOB               -- compressed content
);
"""

SQL_INSERT = """
INSERT OR REPLACE INTO sqlar (name, mode, mtime, sz, data) VALUES (?, ?, ?, ?, ?);
"""


def sqlar_compress(data: bytes) -> bytes:
    compressed = zlib.compress(data, level=-1)

    if len(compressed) < len(data):
        return compressed

    return data


def sqlar_uncompress(data: bytes, size: int) -> bytes:
    if size == len(data):
        return data

    return zlib.decompress(data)


def is_sqlar(cursor: sqlite3.Cursor) -> bool:
    cursor.execute('PRAGMA table_info("sqlar")')

    return cursor.fetchall() == SQLAR_TABLE_EXPECTED_RESULT


def get_safe_path(name: str) -> str:
    return str(Path(name).as_posix())


@dataclass
class SQLiteArchiveRecord:
    __slots__ = ("name", "mode", "mtime", "size", "data")

    name: str
    mode: int
    mtime: int
    size: int
    data: bytes

    @property
    def is_compressed(self) -> bool:
        return self.size != len(self.data)

    @property
    def uncompressed_data(self) -> bytes:
        return sqlar_uncompress(self.data, self.size)

    @property
    def is_dir(self) -> bool:
        return self.size == 0

    @property
    def is_symlink(self) -> bool:
        return self.size == -1

    @property
    def is_file(self) -> bool:
        return self.size > 0


# NOTE: this class is threadsafe but does not allow for any concurrent access
class SQLiteArchive:
    in_memory: bool
    lock: Lock
    connection: sqlite3.Connection
    default_mode: int

    def __init__(self, filename: Optional[str] = None):
        self.in_memory = False
        self.default_mode = 0o664

        already_exists = False

        if filename is None:
            self.in_memory = True
            filename = ":memory:"
        else:
            already_exists = isfile(filename)

        self.connection = sqlite3.connect(filename, check_same_thread=False)
        self.lock = Lock()

        if not self.in_memory:
            self.default_mode = stat(filename).st_mode & 0o777

        if not already_exists:
            self.connection.executescript(SQL_PRAGMAS)
            self.connection.execute(SQL_CREATE)
            self.connection.commit()
        else:
            with self.transaction() as cursor:
                if not is_sqlar(cursor):
                    raise SQLArchiveInvalidError

    @contextmanager
    def transaction(self):
        cursor = None

        try:
            with self.lock, self.connection:
                cursor = self.connection.cursor()
                yield cursor
        finally:
            if cursor is not None:
                cursor.close()

    def __len__(self) -> int:
        with self.transaction() as cursor:
            cursor.execute("SELECT count(*) FROM sqlar;")
            return cursor.fetchone()[0]

    def write(self, name: str, data: bytes, mtime: Optional[int] = None) -> None:
        with self.transaction() as cursor:
            safe_path = get_safe_path(name)
            compressed_data = sqlar_compress(data)
            mtime = int(datetime.utcnow().timestamp()) if mtime is None else mtime

            cursor.execute(
                SQL_INSERT,
                (safe_path, self.default_mode, mtime, len(data), compressed_data),
            )

    def read(self, name: str) -> SQLiteArchiveRecord:
        with self.transaction() as cursor:
            cursor.execute(
                "SELECT * FROM sqlar WHERE name = ? LIMIT 1;", (get_safe_path(name),)
            )

            row = cursor.fetchone()

            if row is None:
                raise KeyError(name)

            return SQLiteArchiveRecord(*row)

    def __iter__(self) -> Iterator[SQLiteArchiveRecord]:
        with self.transaction() as cursor:
            cursor.execute("SELECT * FROM sqlar;")

            for row in iterate_over_sqlite_cursor(cursor):
                yield SQLiteArchiveRecord(*row)

    def close(self):
        self.connection.close()

    def __del__(self):
        self.close()
