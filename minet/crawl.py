# =============================================================================
# Minet Crawl
# =============================================================================
#
# Functions related to the crawling utilities of minet.
#
from queue import Queue
from persistqueue import SQLiteQueue
from quenouille import imap_unordered, iter_queue
from ural import get_domain_name

from minet.utils import create_pool, request

from minet.defaults import (
    DEFAULT_GROUP_PARALLELISM,
    DEFAULT_GROUP_BUFFER_SIZE,
    DEFAULT_THROTTLE
)


class CrawlJob(object):
    __slots__ = ('url')

    def __init__(self, url):
        self.url = url


class Spider(object):
    def __init__(self, definition):
        self.definition = definition


def crawl(spec, queue_path=None, threads=25, buffer_size=DEFAULT_GROUP_BUFFER_SIZE,
          throttle=DEFAULT_THROTTLE):

    # Memory queue
    if queue_path is None:
        queue = Queue()

    # Persistent queue
    else:
        queue = SQLiteQueue(queue_path, auto_commit=True, multithreading=True)

    # Finding start urls
    start_urls = [spec['start_url']]

    for url in start_urls:
        queue.put(CrawlJob(url))

    http = create_pool(
        num_pools=threads * 2,
        maxsize=1
    )

    def grouper(job):
        return get_domain_name(job.url)

    def worker(job):
        return request(http, job.url)

    queue_iterator = iter_queue(queue)

    multithreaded_iterator = imap_unordered(
        queue_iterator,
        worker,
        threads,
        group=grouper,
        group_parallelism=DEFAULT_GROUP_PARALLELISM,
        group_buffer_size=buffer_size,
        group_throttle=throttle
    )

    for result in multithreaded_iterator:
        print(result)
