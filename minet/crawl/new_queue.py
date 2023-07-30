from typing import Counter, Dict, Iterable, Iterator, List, Tuple, Optional

import sqlite3
import pickle
from os import makedirs
from os.path import join, isfile
from shutil import rmtree
from queue import Empty
from threading import Lock
from contextlib import contextmanager
from datetime import datetime

from minet.crawl.types import CrawlJob


SQL_CREATE = """
PRAGMA journal_mode=wal;

CREATE TABLE "queue" (
    "index" INTEGER PRIMARY KEY,
    "status" INTEGER NOT NULL DEFAULT 0,
    "id" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "group" TEXT,
    "depth" INTEGER NOT NULL,
    "spider" TEXT,
    "priority" INTEGER NOT NULL,
    "data" BLOB,
    "parent" TEXT
);
CREATE INDEX "idx_queue_priority_index" ON "queue" ("priority", "index");
CREATE INDEX "idx_queue_group" ON "queue" ("group");
CREATE INDEX "idx_queue_status" ON "queue" ("status");

CREATE TABLE "throttle" (
    "group" TEXT PRIMARY KEY,
    "timestamp" REAL NOT NULL
) WITHOUT ROWID;

CREATE TABLE "parallelism" (
    "group" TEXT PRIMARY KEY,
    "count" INTEGER NOT NULL
) WITHOUT ROWID;
"""

SQL_INSERT_JOB = """
INSERT INTO "queue" (
    "index",
    "id",
    "url",
    "group",
    "depth",
    "spider",
    "priority",
    "data",
    "parent"
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

SQL_GET_JOB = """
SELECT
    "queue"."index",
    "queue"."id",
    "queue"."url",
    "queue"."group",
    "queue"."depth",
    "queue"."spider",
    "queue"."priority",
    "queue"."data",
    "queue"."parent"
FROM "queue"
LEFT JOIN "throttle" ON "queue"."group" = "throttle"."group"
LEFT JOIN "parallelism" ON "queue"."group" = "parallelism"."group"
WHERE (
   "queue"."status" = 0
   AND ("throttle"."timestamp" IS NULL OR "throttle"."timestamp" <= ?)
   AND ("parallelism"."count" IS NULL OR "parallelism"."count" < ?)
)
ORDER BY "priority" ASC, "index" %s
LIMIT 1;
"""

SQL_INCREMENT_PARALLELISM = """
INSERT OR REPLACE INTO "parallelism" ("group", "count") VALUES (
    ?,
    COALESCE((SELECT ("count" + 1) FROM "parallelism" WHERE "group" = ? LIMIT 1), 1)
)
"""


# TODO: the database should probably drop useless throttle info + parallelism + vacuum
# once every task operation
class CrawlerQueue:
    # Params
    persistent: bool
    resuming: bool
    is_lifo: bool
    group_parallelism: int

    # State
    tasks: Dict[CrawlJob, int]
    connection: sqlite3.Connection
    counter: int
    cleanup_interval: int
    put_lock: Lock
    task_lock: Lock

    def __init__(
        self,
        path: Optional[str] = None,
        db_name: str = "queue.db",
        resume: bool = False,
        lifo: bool = False,
        group_parallelism: int = 1,
        cleanup_interval: int = 1000,
    ):
        self.persistent = True
        self.resuming = False

        if path is None:
            self.persistent = False
            full_path = ":memory:"
        else:
            full_path = join(path, db_name)

            if not resume:
                rmtree(path, ignore_errors=True)
                makedirs(path, exist_ok=True)
            elif isfile(full_path):
                self.resuming = True

        self.tasks = {}

        self.is_lifo = lifo
        self.group_parallelism = group_parallelism

        self.cleanup_interval = cleanup_interval
        self.counter = 0
        self.current_task_done_count = 0

        self.put_lock = Lock()
        self.task_lock = Lock()

        self.connection = sqlite3.connect(full_path, check_same_thread=False)

        # Setup
        if not self.resuming:
            self.connection.executescript(SQL_CREATE)
            self.connection.commit()
        else:
            with self.transaction(self.task_lock) as cursor:

                # We need to restart our counter
                cursor.execute('SELECT max("index") FROM "queue";')
                self.counter = cursor.fetchone()[0]

                # We can safely drop parallelism info as it is bound to runtime
                cursor.execute('DELETE FROM "parallelism";')
                cursor.execute("VACUUM;")

    @contextmanager
    def transaction(self, lock: Lock):
        try:
            with lock, self.connection:
                cursor = self.connection.cursor()
                yield cursor
        finally:
            cursor.close()

    def iterator_transaction(
        self, lock: Lock, query: str, params: Tuple = tuple()
    ) -> Iterator[List]:
        with self.transaction(lock) as cursor:
            cursor.execute(query, params)

            while True:
                rows = cursor.fetchmany(128)

                if not rows:
                    return

                for row in rows:
                    yield row

    def __count(self, cursor: sqlite3.Cursor) -> int:
        cursor.execute('SELECT count(*) FROM "queue" WHERE "status" = 0;')
        return cursor.fetchone()[0]

    def qsize(self) -> int:
        with self.transaction(self.task_lock) as cursor:
            return self.__count(cursor)

    def __len__(self) -> int:
        return self.qsize()

    def put_many(self, jobs: Iterable[CrawlJob]) -> int:
        with self.transaction(self.put_lock) as cursor:
            rows = []

            for job in jobs:
                rows.append(
                    (
                        self.counter,
                        job.id,
                        job.url,
                        job.group,
                        job.depth,
                        job.spider,
                        job.priority,
                        pickle.dumps(job.data) if job.data is not None else None,
                        job.parent,
                    )
                )
                self.counter += 1

            cursor.executemany(SQL_INSERT_JOB, rows)
            return cursor.rowcount

    def put(self, job: CrawlJob) -> None:
        self.put_many((job,))

    def get(self, block: bool = True) -> CrawlJob:
        if block:
            raise NotImplementedError

        with self.transaction(self.task_lock) as cursor:
            cursor.execute(
                SQL_GET_JOB % ("ASC" if not self.is_lifo else "DESC"),
                (datetime.now(), self.group_parallelism),
            )
            row = cursor.fetchone()

            if row is None:
                # Queue really is drained
                if self.__count(cursor) == 0:
                    raise Empty

                # We may need to wait for a suitable job
                # TODO: wait through condition with timeout, wrap in while

            index = row[0]

            # NOTE: sqlite does not always support LIMIT on UPDATE
            cursor.execute(
                'UPDATE "queue" SET "status" = 1 WHERE "index" = ?;',
                (index,),
            )

            job = CrawlJob(
                row[2],
                id=row[1],
                group=row[3],
                depth=row[4],
                spider=row[5],
                priority=row[6],
                data=pickle.loads(row[7]) if row[7] is not None else None,
                parent=row[8],
            )

            # TODO: callable group parallelism
            if job.group is not None:
                cursor.execute(SQL_INCREMENT_PARALLELISM, (job.group, job.group))

            # NOTE: jobs are hashable by id
            self.tasks[job] = index

            return job

    # NOTE: we will need to cheat a little bit to work with quenouille here.
    # This method will actually block but raise Empty if the queue is drained.
    # We will also need to handle throttling and group parallelism
    # on our own and use buffer_size=0 on quenouille's size to bypass the
    # optimistic buffer that trumps the true ordering of the given queue.
    def get_nowait(self) -> CrawlJob:
        return self.get(False)

    def worked_groups(self) -> Counter[str]:
        g = Counter()

        for row in self.iterator_transaction(
            self.task_lock,
            'SELECT "group", "count" FROM "parallelism" WHERE "count" > 0;',
        ):
            g[row[0]] = row[1]

        return g

    def __cleanup(self, cursor: sqlite3.Cursor) -> None:
        self.current_task_done_count = 0
        cursor.execute('DELETE FROM "parallelism" WHERE "count" < 1;')
        cursor.execute(
            'DELETE FROM "throttle" WHERE "timestamp" < ?', (datetime.now(),)
        )
        cursor.execute("VACUUM;")

    def task_done(self, job: CrawlJob) -> None:
        with self.transaction(self.task_lock) as cursor:
            index = self.tasks.get(job)

            if index is None:
                raise RuntimeError("job is not being worked")

            cursor.execute('DELETE FROM "queue" WHERE "index" = ? LIMIT 1;', (index,))
            cursor.execute(
                'UPDATE "parallelism" SET "count" = "count" - 1 WHERE "group" = ?;',
                (job.group,),
            )

            # TODO: update throttle info here and validate parallelism = 1

            self.current_task_done_count += 0

            if self.current_task_done_count >= self.cleanup_interval:
                self.__cleanup(cursor)

    def __del__(self) -> None:
        self.connection.close()
