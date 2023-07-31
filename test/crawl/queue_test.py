from pytest import raises
from queue import Empty

from minet.crawl.types import CrawlJob
from minet.crawl.queue import CrawlerQueue


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

        assert queue.worked_groups() == {"A": 2}

        queue.task_done(job2)

        assert queue.worked_groups() == {"A": 1}

        queue.task_done(job1)

        assert queue.worked_groups() == {}
