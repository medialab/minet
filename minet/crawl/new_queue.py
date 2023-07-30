from typing import DefaultDict, List, Iterable, Optional

import sqlite3
import pickle
from os import makedirs
from os.path import join, isfile
from shutil import rmtree
from queue import Empty
from threading import Lock
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from minet.crawl.types import CrawlJob


def timestamp() -> int:
    return int(datetime.now().timestamp())


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
    "timestamp" INTEGER NOT NULL
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

SQL_INSERT_THROTTLE = """
INSERT INTO "throttle" (
    "group",
    "timestamp"
) VALUES (?, ?);
"""

SQL_INSERT_PARALLELISM = """
INSERT INTO "parallelism" (
    "group",
    "count"
) VALUES (?, ?);
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


@dataclass
class CrawlerQueueTask:
    index: int
    job: CrawlJob


# TODO: the database should probably drop useless throttle info + parallelism + vacuum
# once every task operation
class CrawlerQueue:
    # Params
    persistent: bool
    resuming: bool
    is_lifo: bool
    is_optimal: bool
    group_parallelism: int

    # State
    tasks: DefaultDict[Optional[str], List[CrawlerQueueTask]]
    connection: sqlite3.Connection
    count: int
    put_lock: Lock
    task_lock: Lock

    def __init__(
        self,
        path: Optional[str] = None,
        db_name: str = "queue.db",
        resume: bool = False,
        lifo: bool = False,
        optimal: bool = False,
        group_parallelism: int = 1,
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

        self.tasks = DefaultDict(list)

        self.is_lifo = lifo
        self.is_optimal = optimal
        self.group_parallelism = group_parallelism

        self.counter = 0

        self.put_lock = Lock()
        self.task_lock = Lock()

        self.connection = sqlite3.connect(full_path, check_same_thread=False)

        # Setup
        if not self.resuming:
            self.connection.executescript(SQL_CREATE)
            self.connection.commit()
        else:
            with self.transaction(self.task_lock) as cursor:
                cursor.execute('SELECT max("index") FROM "queue";')
                self.counter = cursor.fetchone()[0]
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

    def qsize(self) -> int:
        with self.transaction(self.task_lock) as cursor:
            cursor.execute('SELECT count(*) FROM "queue" WHERE "status" = 0;')
            return cursor.fetchone()[0]

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
                (timestamp(), self.group_parallelism),
            )
            row = cursor.fetchone()

            if row is None:
                raise Empty

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

            self.tasks[job.group].append(CrawlerQueueTask(index, job))

            return job

    # NOTE: we will need to cheat a little bit to work with quenouille here.
    # This method will actually block but raise Empty if the queue is drained.
    # We will also need to handle throttling and group parallelism
    # on our own and use buffer_size=0 on quenouille's size to bypass the
    # optimistic buffer that trumps the true ordering of the given queue.
    def get_nowait(self) -> CrawlJob:
        return self.get(False)

    def task_done(self, job: CrawlJob) -> None:
        with self.transaction(self.task_lock) as cursor:
            task_group = self.tasks.get(job.group)

            if task_group is None:
                raise RuntimeError("job is not being worked")

            task = next((t for t in task_group if t.job.id == job.id), None)

            if task is None:
                raise RuntimeError("job is not being worked")

            if len(task_group) == 1:
                del self.tasks[job.group]
            else:
                self.tasks[job.group] = [t for t in task_group if t is not task]

            cursor.execute('DELETE FROM "queue" WHERE "index" = ? LIMIT 1;')

    def __del__(self) -> None:
        self.connection.close()
