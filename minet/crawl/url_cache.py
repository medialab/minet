from typing import TypeVar, Generic, Set, Iterable, Iterator, List

import sqlite3
from threading import Lock
from contextlib import contextmanager

T = TypeVar("T")


class AtomicSet(Generic[T]):
    """
    A simple set wrapper ensuring all operations are
    atomic and thus threadsafe.
    """

    __items: Set[T]
    __lock: Lock

    def __init__(self):
        self.__items = set()
        self.__lock = Lock()

    def add(self, item: T) -> bool:
        with self.__lock:
            len_before = len(self.__items)

            self.__items.add(item)

            return len(self.__items) > len_before

    def add_many(self, items: Iterable[T]) -> int:
        with self.__lock:
            len_before = len(self.__items)

            for item in items:
                self.__items.add(item)

            return len(self.__items) - len_before

    def __len__(self) -> int:
        with self.__lock:
            return len(self.__items)

    def __contains__(self, item: T) -> bool:
        with self.__lock:
            return item in self.__items

    def __iter__(self) -> Iterator[T]:
        with self.__lock:
            yield from self.__items


class SQLiteStringSet:
    def __init__(self, path):
        self.path = path

        self.__connection = sqlite3.connect(self.path, check_same_thread=False)
        self.__lock = Lock()

        # Setup
        self.__connection.execute("PRAGMA journal_mode=wal;")
        self.__connection.execute(
            'CREATE TABLE IF NOT EXISTS "set" ("key" TEXT PRIMARY KEY);'
        )
        self.__connection.commit()

    @contextmanager
    def __transaction(self):
        try:
            with self.__lock, self.__connection:
                cursor = self.__connection.cursor()
                yield cursor
        finally:
            cursor.close()

    def vacuum(self) -> None:
        with self.__transaction() as cursor:
            cursor.execute("VACUUM;")

    def add(self, item: str) -> bool:
        with self.__transaction() as cursor:
            try:
                cursor.execute('INSERT INTO "set" ("key") VALUES (?);', (item,))
            except sqlite3.IntegrityError:
                return False

            return True

    def add_many(self, items: Iterable[str]) -> int:
        with self.__transaction() as cursor:
            rows = [(item,) for item in items]
            cursor.executemany('INSERT OR IGNORE INTO "set" ("key") VALUES (?);', rows)
            return cursor.rowcount

    # def add_and_keep_new(self, items: Iterable[str]) -> List[str]:
    #     with self.__transaction() as cursor:
    #         rows = [(item,) for item in items]
    #         cursor.executemany('SELECT "key" FROM "set" WHERE "key" = ?;', rows)
    #         print(cursor.fetchall())

    def __contains__(self, item: str) -> bool:
        with self.__transaction() as cursor:
            cursor.execute('SELECT 1 FROM "set" WHERE "key" = ?;', (item,))
            return cursor.fetchone() is not None

    def __len__(self) -> int:
        with self.__transaction() as cursor:
            cursor.execute('SELECT COUNT(*) FROM "set";')
            return cursor.fetchone()[0]

    def __iter__(self) -> Iterator[str]:
        with self.__transaction() as cursor:
            cursor.execute('SELECT "key" FROM "set";')

            while True:
                rows = cursor.fetchmany(128)

                if not rows:
                    return

                for row in rows:
                    yield row[0]

    def __del__(self) -> None:
        self.__connection.close()
