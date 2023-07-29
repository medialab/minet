from minet.crawl.new_queue import CrawlerQueue


class TestCrawlerQueue:
    def test_basics(self):
        queue = CrawlerQueue()

        assert queue.qsize() == 0
