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
