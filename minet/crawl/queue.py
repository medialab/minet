from typing import Dict, List, Tuple, Iterable, Iterator, Optional, Callable, Union
from minet.types import Literal

import sqlite3
import pickle
from os import makedirs
from os.path import join, isfile
from shutil import rmtree
from queue import Empty
from threading import Lock, Condition
from contextlib import contextmanager
from datetime import datetime
from random import randint
from dataclasses import dataclass
from quenouille.constants import TIMER_EPSILON

from minet.crawl.types import CrawlJob
from minet.utils import iterate_over_sqlite_cursor

AnyThrottle = Union[float, Callable[[CrawlJob], float]]
AnyParallelism = Union[int, Callable[[CrawlJob], int]]


def now() -> float:
    return datetime.now().timestamp()


# NOTE: synchronous=normal is probably alright for our use-case
SQL_PRAGMAS = """
PRAGMA journal_mode=wal;
PRAGMA synchronous=normal;
"""

# NOTE about status:
# status=0 is to do
# status=1 is doing
# status=2 is done, but kept until cleanup

# NOTE: the multi-index on ("status", "priority", "index") seems
# to be the better one according to the query planner
# NOTE: we are not relying on AUTOINCREMENT because it seems to
# be bad for performance and because our queue can handle it on
# its own. This means that the job having the max index must
# never be deleted for this queue to be able to resume without issue.
SQL_CREATE = """
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
CREATE INDEX "idx_queue_multi" ON "queue" ("status", "priority", "index");

CREATE TABLE "throttle" (
    "group" TEXT PRIMARY KEY,
    "timestamp" REAL NOT NULL
) WITHOUT ROWID;
CREATE INDEX "idx_throttle_timestamp" ON "throttle" ("timestamp");

CREATE TABLE "parallelism" (
    "group" TEXT PRIMARY KEY,
    "count" INTEGER NOT NULL,
    "allowed" INTEGER NOT NULL
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

# NOTE: we thought about the opportunity of using
# RIGHT JOIN as further optimization but it cannot work
# without keeping a reference to all the groups in the "throttle"
# and "parallelism" table at all time and this is hardly optimal
# regarding disk space and query time, in spite of indices.
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
   AND ("parallelism"."count" IS NULL OR "parallelism"."count" < "parallelism"."allowed")
)
ORDER BY "priority" ASC, "index" %s
LIMIT 1;
"""

SQL_DUMP = """
SELECT
    "index",
    "id",
    "url",
    "group",
    "depth",
    "spider",
    "priority",
    "data",
    "parent",
    "status"
FROM "queue"
ORDER BY "index";
"""

# NOTE: we thought about having a single allowance column that would
# be decremented when worked by threads but it means we need to keep
# a reference for each group in the "parallelism" table at all time
# for this to work and this is hardly optimal regarding disk space
# and query time, in spite of indices.
SQL_INCREMENT_PARALLELISM = """
INSERT OR REPLACE INTO "parallelism" ("group", "count", "allowed") VALUES (
    ?,
    COALESCE((SELECT ("count" + 1) FROM "parallelism" WHERE "group" = ? LIMIT 1), 1),
    ?
)
"""

SQL_UPDATE_THROTTLE = """
INSERT OR REPLACE INTO "throttle" ("group", "timestamp") VALUES (?, ?);
"""

CrawlerQueueJobStatus = Literal["todo", "doing", "done"]


@dataclass
class CrawlerQueueRecord:
    index: int
    status: CrawlerQueueJobStatus
    job: CrawlJob

    @staticmethod
    def fieldnames():
        return ["index", "status"] + CrawlJob.fieldnames()

    def __csv_row__(self) -> List:
        row = [self.index, self.status] + list(self.job.__csv_row__())
        return row


# NOTE: this exception is only used when we need to manually
# unblock the queue, e.g. when quenouille must teardown
class BrokenCrawlerQueue(Exception):
    pass


# TODO: tests with null group


# NOTE: this queue can be used by `quenouille` but since it handles
# group parallelism and throttling on its own, we must shunt it on
# `quenouille` side. Also, keep in mind that buffer_size must be
# set to 0 to keep the queue ordering consistent and bypass `quenouille`
# optimistic buffer that is tailored for lazy iterable, not processing
# queues.
# NOTE: this queue does not follow python's queue.Queue semantics exactly
# because its #.get method can block, but will raise Empty when drained.
# This is fine with `quenouille` if we don't forget to call #.unblock
# on panic.
# NOTE: sqlite needs to serialize writes, which means it is not particularly
# useful in our case to allow for concurrent access to the queue because most
# of its operations need to update the database somehow. This also means we
# can rely on a single lock to make multithreaded transactions safe.
class CrawlerQueue:
    # Params
    persistent: bool
    resuming: bool
    is_lifo: bool
    group_parallelism: AnyParallelism
    throttle: AnyThrottle

    # State
    tasks: Dict[str, int]
    connection: sqlite3.Connection
    counter: int
    cleanup_interval: int
    vacuum_interval: int
    waiter: Condition
    currently_waiting_count: int
    transaction_lock: Lock
    broken: bool

    def __init__(
        self,
        path: Optional[str] = None,
        db_name: str = "queue.db",
        resume: bool = False,
        inspect: bool = False,
        lifo: bool = False,
        group_parallelism: AnyParallelism = 1,
        throttle: AnyThrottle = 0,
        cleanup_interval: int = 1000,
        vacuum_interval: int = 10_000,
    ):
        self.persistent = True
        self.resuming = False

        if path is None:
            if inspect:
                raise TypeError("cannot inspect a memory queue")

            self.persistent = False
            # NOTE: I am not sure this is advisable most of the time
            full_path = "file:%i-%i.db?mode=memory&cache=shared" % (
                id(self),
                randint(0, 2**32 - 1),
            )
        else:
            full_path = join(path, db_name)

            if inspect:
                if not isfile(full_path):
                    raise RuntimeError(
                        "sqlite database for queue does not exist and cannot be inspected"
                    )
            elif not resume:
                rmtree(path, ignore_errors=True)
            elif isfile(full_path):
                self.resuming = True

            makedirs(path, exist_ok=True)

        self.tasks = {}

        self.is_lifo = lifo

        self.group_parallelism = group_parallelism
        self.throttle = throttle

        self.cleanup_interval = cleanup_interval
        self.vacuum_interval = vacuum_interval
        self.counter = 0
        self.current_task_done_count = 0

        self.waiter = Condition()
        self.currently_waiting_count = 0
        self.transaction_lock = Lock()
        self.broken = False

        self.connection = sqlite3.connect(full_path, check_same_thread=False)

        # NOTE: it's seems it is safer and common practice to
        # reexecute pragmas each time because they might not
        # be stored persistently in some instances.
        self.connection.executescript(SQL_PRAGMAS)
        self.connection.commit()

        if inspect:
            return

        # Setup
        with self.transaction() as cursor:
            if not self.resuming:
                cursor.executescript(SQL_CREATE)
            else:
                # We need to restart our counter
                cursor.execute('SELECT max("index") FROM "queue";')
                self.counter = cursor.fetchone()[0] + 1

                # We need to clear status=1
                # NOTE: we don't clear status > 1 just in case we need to use those
                # to indicate something else
                cursor.execute('UPDATE "queue" SET "status" = 0 WHERE "status" = 1;')

                # We can safely drop parallelism info as it is bound to runtime
                cursor.execute('DELETE FROM "parallelism";')

                # Cleanup throttle a bit
                cursor.execute('DELETE FROM "throttle" WHERE "timestamp" < ?', (now(),))

                cursor.connection.commit()
                cursor.execute("VACUUM;")

    @contextmanager
    def transaction(self):
        cursor = None
        try:
            with self.transaction_lock, self.connection:
                cursor = self.connection.cursor()
                yield cursor
        finally:
            if cursor is not None:
                cursor.close()

    def explain_query_plan(self, sql: str) -> str:
        if sql == "get":
            sql = SQL_GET_JOB % ("ASC" if not self.is_lifo else "DESC")

        sql = sql.replace("?", "1")

        with self.transaction() as cursor:
            cursor.execute("EXPLAIN QUERY PLAN %s" % sql)

            return "\n".join(row[3] for row in iterate_over_sqlite_cursor(cursor))

    def __count(self, cursor: sqlite3.Cursor) -> int:
        cursor.execute('SELECT count(*) FROM "queue" WHERE "status" = 0;')
        return cursor.fetchone()[0]

    def qsize(self) -> int:
        with self.transaction() as cursor:
            return self.__count(cursor)

    def __len__(self) -> int:
        return self.qsize()

    def put_many(self, jobs: Iterable[CrawlJob]) -> int:
        with self.transaction() as cursor:
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

            # NOTE: executemany prepares the statement for us
            cursor.executemany(SQL_INSERT_JOB, rows)
            count = cursor.rowcount

        # NOTE: we notify the waiter because adding jobs to the queue means
        # there might be one we can do right now
        with self.waiter:
            self.waiter.notify()

        return count

    def put(self, job: CrawlJob) -> None:
        self.put_many((job,))

    # NOTE: we will need to cheat a little bit to work with quenouille here.
    # This method will actually block but raise Empty if the queue is drained.
    # We will also need to handle throttling and group parallelism
    # on our own and use buffer_size=0 on quenouille's size to bypass the
    # optimistic buffer that trumps the true ordering of the given queue.
    def get(self, block=True) -> CrawlJob:
        if block:
            raise NotImplementedError

        need_to_wait = False
        need_to_wait_for_at_least = None

        while True:
            # Waiting?
            # NOTE: we wait here so we can: 1. avoid recursion and 2. release
            # the transaction lock to avoid an obvious deadlock.
            if need_to_wait:
                with self.waiter:
                    self.currently_waiting_count += 1
                    self.waiter.wait(need_to_wait_for_at_least)
                    self.currently_waiting_count -= 1

                need_to_wait = False
                need_to_wait_for_at_least = None

                # NOTE: this only happens when unblocking manually and
                # usually the queue won't be used anymore afterwards.
                # If we finally understand the contrary, we should
                # add some #.repair method or change threading paradigm.
                if self.broken:
                    raise BrokenCrawlerQueue

            with self.transaction() as cursor:
                cursor.execute(
                    SQL_GET_JOB % ("ASC" if not self.is_lifo else "DESC"),
                    (now(),),
                )
                row = cursor.fetchone()

                if row is None:
                    # Queue really is drained
                    if self.__count(cursor) == 0:
                        raise Empty

                    # We may need to wait for a suitable job
                    # NOTE: here we may wait either for one slot to become
                    # open wrt parallelism or enough time wrt throttling
                    need_to_wait = True

                    cursor.execute('SELECT min("timestamp") FROM "throttle" LIMIT 1;')
                    throttle_row = cursor.fetchone()

                    if throttle_row is not None and throttle_row[0] is not None:
                        need_to_wait_for_at_least = (
                            max(0, throttle_row[0] - now()) + TIMER_EPSILON
                        )

                    continue

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

                if job.group is not None:
                    allowed = self.group_parallelism

                    if callable(allowed):
                        allowed = allowed(job)

                    cursor.execute(
                        SQL_INCREMENT_PARALLELISM,
                        (job.group, job.group, allowed),
                    )

                self.tasks[job.id] = index

                return job

    def get_nowait(self) -> CrawlJob:
        return self.get(False)

    def unblock(self) -> None:
        with self.waiter:
            if self.currently_waiting_count == 0:
                return

            self.broken = True
            self.waiter.notify_all()

    def worked_groups(self) -> Dict[str, Tuple[int, int]]:
        g = {}

        with self.transaction() as cursor:
            cursor.execute(
                'SELECT "group", "count", "allowed" FROM "parallelism" WHERE "count" > 0;'
            )

            for row in iterate_over_sqlite_cursor(cursor):
                g[row[0]] = (row[1], row[2])

        return g

    def dump(self) -> Iterator[CrawlerQueueRecord]:
        with self.transaction() as cursor:
            cursor.execute(SQL_DUMP)

            for row in iterate_over_sqlite_cursor(cursor):
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

                status_code = row[9]
                status = "todo"

                if status_code == 1:
                    status = "doing"
                elif status_code == 2:
                    status = "done"

                yield CrawlerQueueRecord(index=row[0], status=status, job=job)

    def __cleanup(self, cursor: sqlite3.Cursor) -> None:
        # NOTE: we make sure to keep the last index given to ensure we can resume safely
        cursor.execute(
            'DELETE FROM "queue" WHERE "status" = 2 AND "index" <> (SELECT max("index") FROM "queue" ORDER BY "index");'
        )
        cursor.execute('DELETE FROM "parallelism" WHERE "count" < 1;')
        cursor.execute('DELETE FROM "throttle" WHERE "timestamp" < ?', (now(),))

    def __clear(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute('DELETE FROM "queue";')
        cursor.execute('DELETE FROM "parallelism";')
        cursor.execute('DELETE FROM "throttle";')

    def __vacuum_and_analyze(self, cursor: sqlite3.Cursor) -> None:
        cursor.execute("PRAGMA analysis_limit=1000;")
        cursor.execute("PRAGMA optimize;")
        cursor.connection.commit()
        cursor.execute("VACUUM;")
        cursor.connection.commit()

    def cleanup(self) -> None:
        with self.transaction() as cursor:
            self.__cleanup(cursor)

    def clear(self) -> None:
        with self.transaction() as cursor:
            self.__clear(cursor)

    # NOTE: there is a subtle difference between #.release_group
    # and #.task_done. The first indicates to the queue that we
    # finished network actions related to the given group so
    # we can update parallelism & throttling info. The latter that
    # the task is completely done, i.e. after outputs were flushed
    # in the crawler loop so that we can safely forget about the given
    # task. This is important to ensure atomicity as well as possible.
    # Without creating backpressure on the queue's constraints.
    def release_group(self, job: CrawlJob) -> None:
        with self.transaction() as cursor:
            if job.id not in self.tasks:
                raise RuntimeError("job is not being worked")

            cursor.execute(
                'UPDATE "parallelism" SET "count" = "count" - 1 WHERE "group" = ?;',
                (job.group,),
            )

            # NOTE: null group is not throttled, the same as `quenouille`
            if job.group is not None:
                throttle = self.throttle

                if callable(throttle):
                    throttle = throttle(job)

                if throttle > 0:
                    cursor.execute(SQL_UPDATE_THROTTLE, (job.group, now() + throttle))

        # We notify one waiter that parallelism was updated
        with self.waiter:
            self.waiter.notify()

    @contextmanager
    def group_releaser(self, job: CrawlJob):
        try:
            yield
        finally:
            self.release_group(job)

    def task_done(self, job: CrawlJob) -> None:
        with self.transaction() as cursor:
            index = self.tasks.pop(job.id, None)

            if index is None:
                raise RuntimeError("job is not being worked")

            cursor.execute(
                'UPDATE "queue" SET "status" = 2 WHERE "index" = ?;', (index,)
            )

            self.current_task_done_count += 1

            if self.current_task_done_count % self.cleanup_interval == 0:
                self.__cleanup(cursor)

            if self.current_task_done_count % self.vacuum_interval == 0:
                self.__vacuum_and_analyze(cursor)

    def close(self) -> None:
        self.connection.close()

    def __del__(self) -> None:
        self.close()
