from typing import List

from pytest import raises
from queue import Empty

from minet.crawl.types import CrawlJob
from minet.crawl.queue import CrawlerQueue, CrawlerQueueRecord


# Beware: this may block if you are not careful
def consume(q: CrawlerQueue) -> List[CrawlJob]:
    jobs = []

    while True:
        try:
            jobs.append(q.get_nowait())
        except Empty:
            break

    return jobs


class TestCrawlerQueue:
    def test_basics(self):
        queue = CrawlerQueue()

        assert queue.qsize() == 0
        assert len(queue) == 0

        with raises(Empty):
            queue.get_nowait()

        job = CrawlJob("https://lemonde.fr")

        queue.put(job)

        assert len(queue) == 1

        assert queue.get_nowait() == job
        assert len(queue) == 0

        with raises(Empty):
            queue.get_nowait()

        queue.put(CrawlJob("https://lefigaro.fr"))

        jobs = list(queue.dump())

        assert [(j.index, j.status) for j in jobs] == [(0, "doing"), (1, "todo")]

    def test_worked_groups(self):
        queue = CrawlerQueue(group_parallelism=2)

        job1 = CrawlJob("https://lemonde.fr", group="A")
        job2 = CrawlJob("https://lefigaro.fr", group="A")

        queue.put(job1)
        queue.put(job2)

        queue.get_nowait()
        queue.get_nowait()

        assert queue.worked_groups() == {"A": (2, 2)}

        queue.release_group(job1)

        assert queue.worked_groups() == {"A": (1, 2)}

        queue.release_group(job2)

        assert queue.worked_groups() == {}

    def test_fifo_lifo_order(self):
        job1 = CrawlJob("A", group="A")
        job2 = CrawlJob("B", group="B")
        job3 = CrawlJob("C", group="C")
        job4 = CrawlJob("D", group="D")
        job5 = CrawlJob("E", group="E")

        jobs = [job1, job2, job3, job4, job5]

        queue = CrawlerQueue()
        queue.put_many(jobs)

        output = consume(queue)

        assert output == jobs

        queue = CrawlerQueue(lifo=True)
        queue.put_many(jobs)

        output = consume(queue)

        assert output == list(reversed(jobs))

    def test_priority_order(self):
        job1 = CrawlJob("A", group="A", priority=2)
        job2 = CrawlJob("B", group="B", priority=4)
        job3 = CrawlJob("C", group="C", priority=0)
        job4 = CrawlJob("D", group="D", priority=5)
        job5 = CrawlJob("E", group="E", priority=1)
        job6 = CrawlJob("F", group="F", priority=5)

        jobs = [job1, job2, job3, job4, job5, job6]

        queue = CrawlerQueue()
        queue.put_many(jobs)

        output = consume(queue)

        assert output == [job3, job5, job1, job2, job4, job6]

        queue = CrawlerQueue(lifo=True)
        queue.put_many(jobs)

        output = consume(queue)
        assert output == [job3, job5, job1, job2, job6, job4]

    def test_resuming(self, tmp_path):
        job1 = CrawlJob("A", group="A")
        job2 = CrawlJob("B", group="B")
        job3 = CrawlJob("C", group="C")

        queue = CrawlerQueue(tmp_path, cleanup_interval=1, vacuum_interval=1)

        queue.put(job1)
        queue.put(job2)
        queue.put(job3)

        assert len(queue) == 3

        assert queue.get_nowait() == job1

        assert len(queue) == 2

        del queue

        queue = CrawlerQueue(
            tmp_path, cleanup_interval=1, vacuum_interval=1, resume=True
        )

        assert len(queue) == 3

        assert queue.get_nowait() == job1
        queue.task_done(job1)

        del queue

        queue = CrawlerQueue(
            tmp_path, cleanup_interval=1, vacuum_interval=1, resume=True
        )

        assert queue.get_nowait() == job2
        assert queue.get_nowait() == job3

        queue.task_done(job2)
        queue.task_done(job3)

        assert len(queue) == 0

        del queue

        queue = CrawlerQueue(
            tmp_path, cleanup_interval=1, vacuum_interval=1, resume=True
        )

        assert len(queue) == 0

        queue.put(job1)

        # NOTE: the queue always retain highest index to be able to resume
        assert list(queue.dump()) == [
            CrawlerQueueRecord(index=2, status="done", job=job3),
            CrawlerQueueRecord(index=3, status="todo", job=job1),
        ]

        queue.get_nowait()
        queue.task_done(job1)

        assert list(queue.dump()) == [
            CrawlerQueueRecord(index=3, status="done", job=job1),
        ]

    def test_memory_leak(self):
        queue = CrawlerQueue()

        queue.put(CrawlJob("http://lemonde.fr"))
        job = queue.get_nowait()

        assert len(queue.tasks) == 1

        queue.task_done(job)

        assert len(queue.tasks) == 0
