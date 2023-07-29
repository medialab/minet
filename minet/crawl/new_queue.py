from typing import DefaultDict, List, Iterable, Optional, Tuple

import sqlite3
from os import makedirs
from os.path import join, isfile
from shutil import rmtree
from queue import PriorityQueue
from threading import Lock
from contextlib import contextmanager

from minet.crawl.types import CrawlJob

# NOTE: I don't think the queue can work with optimal=True, so this class
# is never used in practice
class TransientCrawlerQueue:
    def __init__(self, lifo=False, optimal=False, group_parallelism: int = 1):
        self.tasks: DefaultDict[Optional[str], List[str]] = DefaultDict(list)
        self.queue: PriorityQueue[Tuple[int, int, CrawlJob]] = PriorityQueue()

        self.is_lifo = lifo
        self.is_optimal = optimal
        self.group_parallelism = group_parallelism

        self.counter = 0

        self.put_lock = Lock()
        self.task_lock = Lock()

    def __len__(self) -> int:
        return self.queue.qsize()

    def qsize(self) -> int:
        return self.queue.qsize()

    def put_many(self, jobs: Iterable[CrawlJob]) -> None:
        with self.put_lock:
            for job in jobs:
                queue_item = (job.priority, self.counter, job)
                self.queue.put_nowait(queue_item)

                self.counter += -1 if self.is_lifo else 1

    def put(self, job: CrawlJob) -> None:
        return self.put_many((job,))

    def get(self, block=True) -> CrawlJob:
        with self.task_lock:
            _, _, job = self.queue.get(block)

            # Job is now being worked
            self.tasks[job.group].append(job.id)

            return job

    def get_nowait(self) -> CrawlJob:
        return self.get(False)

    def task_done(self, job: CrawlJob) -> None:
        with self.task_lock:

            task_group = self.tasks.get(job.group)

            if task_group is None or job.id not in task_group:
                raise RuntimeError("job was not being worked")

            if len(task_group) == 1:
                del self.tasks[job.group]
            else:
                task_group.remove(job.id)

            self.queue.task_done()


SQL_CREATE_TABLE = """
PRAGMA journal_mode=wal;
CREATE TABLE "crawler_queue" (
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
CREATE INDEX "idx_priority" ON "crawler_queue" ("priority");
CREATE INDEX "idx_group" ON "crawler_queue" ("group");
CREATE INDEX "idx_status" ON "crawler_queue" ("status");
"""

# IMPORTANT: when resuming we need to read max index!
# IMPORTANT: optimize multi index later


class CrawlerQueue:
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

        self.tasks: DefaultDict[Optional[str], List[str]] = DefaultDict(list)

        self.is_lifo = lifo
        self.is_optimal = optimal
        self.group_parallelism = group_parallelism

        self.counter = 0

        self.put_lock = Lock()
        self.task_lock = Lock()

        self.connection = sqlite3.connect(full_path, check_same_thread=False)

        # Setup
        if not self.resuming:
            self.connection.executescript(SQL_CREATE_TABLE)
            self.connection.commit()

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
            cursor.execute('SELECT count(*) FROM "crawler_queue";')
            return cursor.fetchone()[0]
