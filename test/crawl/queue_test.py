from typing import List

from pytest import raises
from queue import Empty

from minet.crawl.types import CrawlJob
from minet.crawl.queue import CrawlerQueue


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

        queue.task_done(job2)

        assert queue.worked_groups() == {"A": (1, 2)}

        queue.task_done(job1)

        assert queue.worked_groups() == {}

    def test_fifo_lifo(self):
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
