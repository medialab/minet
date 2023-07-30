from typing import Iterator, Any

from sqlite3 import Cursor


def iterate_over_cursor(cursor: Cursor) -> Iterator[Any]:
    while True:
        rows = cursor.fetchmany(128)

        if not rows:
            return

        for row in rows:
            yield row
