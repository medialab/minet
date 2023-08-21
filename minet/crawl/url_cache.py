from typing import (
    TypeVar,
    Generic,
    Set,
    Iterable,
    Iterator,
    List,
    Optional,
    Callable,
    overload,
)

import sqlite3
from os import makedirs
from os.path import join
from threading import Lock
from contextlib import contextmanager
from ebbe import distinct
from ural import canonicalize_url, normalize_url

from minet.crawl.types import CrawlJob, CrawlJobDataType
from minet.utils import iterate_over_sqlite_cursor

T = TypeVar("T")
I = TypeVar("I")


class AtomicSet(Generic[T]):
    """
    A simple set wrapper ensuring all operations are
    atomic and thus threadsafe.
    """

    __items: Set[T]
    lock: Lock

    def __init__(self):
        self.__items = set()
        self.lock = Lock()

    def add(self, item: T) -> bool:
        with self.lock:
            len_before = len(self.__items)

            self.__items.add(item)

            return len(self.__items) > len_before

    def add_many(self, items: Iterable[T]) -> int:
        with self.lock:
            len_before = len(self.__items)

            for item in items:
                self.__items.add(item)

            return len(self.__items) - len_before

    @overload
    def add_many_and_keep_new(
        self, items: Iterable[I], key: Callable[[I], T] = ...
    ) -> List[I]:
        ...

    @overload
    def add_many_and_keep_new(self, items: Iterable[T], key: None = ...) -> List[T]:
        ...

    def add_many_and_keep_new(self, items, key=None):
        with self.lock:
            new = []

            for item in items:
                k = item if key is None else key(item)

                len_before = len(self.__items)
                self.__items.add(k)

                if len_before < len(self.__items):
                    new.append(item)

            return new

    def __len__(self) -> int:
        with self.lock:
            return len(self.__items)

    def __contains__(self, item: T) -> bool:
        with self.lock:
            return item in self.__items

    def __iter__(self) -> Iterator[T]:
        with self.lock:
            yield from self.__items

    def close(self) -> None:
        pass


# NOTE: synchronous=normal is probably alright for our use-case
SQL_CREATE = """
PRAGMA journal_mode=wal;
PRAGMA synchronous=normal;
CREATE TABLE IF NOT EXISTS "set" (
    "key" TEXT PRIMARY KEY
) WITHOUT ROWID;
"""


class SQLiteStringSet:
    def __init__(self, path: str, db_name: str = "set.db"):
        makedirs(path, exist_ok=True)

        self.path = path

        self.connection = sqlite3.connect(
            join(self.path, db_name), check_same_thread=False
        )
        self.lock = Lock()

        # Setup
        # NOTE: this is reexecuted on resume and this is fine
        # NOTE: it seems it's safer to reexecute pragmas anyway
        self.connection.executescript(SQL_CREATE)
        self.connection.commit()

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

    def add(self, item: str) -> bool:
        with self.transaction() as cursor:
            try:
                cursor.execute('INSERT INTO "set" ("key") VALUES (?);', (item,))
            except sqlite3.IntegrityError:
                return False

            return True

    def add_many(self, items: Iterable[str]) -> int:
        with self.transaction() as cursor:
            rows = [(item,) for item in items]
            cursor.executemany('INSERT OR IGNORE INTO "set" ("key") VALUES (?);', rows)
            return cursor.rowcount

    @overload
    def add_many_and_keep_new(
        self, items: Iterable[I], key: Callable[[I], str] = ...
    ) -> List[I]:
        ...

    @overload
    def add_many_and_keep_new(self, items: Iterable[str], key: None = ...) -> List[str]:
        ...

    def add_many_and_keep_new(self, items, key=None):
        with self.transaction() as cursor:
            new = []

            for item in items:
                try:
                    k = item if key is None else key(item)
                    cursor.execute('INSERT INTO "set" ("key") VALUES (?);', (k,))
                    new.append(item)
                except sqlite3.IntegrityError:
                    pass

            return new

    # NOTE: I keep this for the ugly trick.
    # def contains_many(self, items: Iterable[str]) -> List[str]:
    #     with self.transaction() as cursor:
    #         cursor.execute(
    #             'SELECT "key" FROM "set" WHERE "key" in (SELECT "value" FROM JSON_EACH(?));',
    #             (json.dumps(items),),
    #         )

    def __contains__(self, item: str) -> bool:
        with self.transaction() as cursor:
            cursor.execute('SELECT 1 FROM "set" WHERE "key" = ?;', (item,))
            return cursor.fetchone() is not None

    def __len__(self) -> int:
        with self.transaction() as cursor:
            cursor.execute('SELECT COUNT(*) FROM "set";')
            return cursor.fetchone()[0]

    def __iter__(self) -> Iterator[str]:
        with self.transaction() as cursor:
            cursor.execute('SELECT "key" FROM "set";')

            for row in iterate_over_sqlite_cursor(cursor):
                yield row[0]

    def close(self) -> None:
        self.connection.close()

    def __del__(self) -> None:
        self.close()


class URLCache:
    def __init__(self, path: Optional[str] = None, normalized: bool = False):
        self.path = path
        self.persistent = path is not None
        self.preprocessing = normalize_url if normalized else canonicalize_url
        self.normalized = normalized

        self.__cache = (
            SQLiteStringSet(path, "urls.db") if path is not None else AtomicSet()
        )

    def add(self, url: str) -> bool:
        url = self.preprocessing(url)
        return self.__cache.add(url)

    def register(
        self, jobs: Iterable[CrawlJob[CrawlJobDataType]]
    ) -> List[CrawlJob[CrawlJobDataType]]:
        def url_key(job: CrawlJob[CrawlJobDataType]):
            return self.preprocessing(job.url)

        # We deduplicate beforehand
        jobs = distinct(jobs, key=url_key)
        new = self.__cache.add_many_and_keep_new(jobs, key=url_key)

        return new

    def __len__(self) -> int:
        return len(self.__cache)

    def __iter__(self) -> Iterator[str]:
        return self.__cache.__iter__()

    def __contains__(self, url: str) -> bool:
        url = self.preprocessing(url)
        return url in self.__cache

    def close(self) -> None:
        self.__cache.close()

    def __del__(self) -> None:
        self.close()
