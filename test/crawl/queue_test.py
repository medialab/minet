from pytest import raises
from queue import Empty

from minet.crawl.types import CrawlJob
from minet.crawl.new_queue import CrawlerQueue


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

    def test_worked_groups(self):
        queue = CrawlerQueue(group_parallelism=2)

        queue.put(CrawlJob("https://lemonde.fr", group="A"))
        queue.put(CrawlJob("https://lefigaro.fr", group="A"))

        queue.get_nowait()
        queue.get_nowait()

        assert queue.worked_groups() == {"A": 2}
