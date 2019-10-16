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
from collections import namedtuple

from minet.scrape import Scraper
from minet.utils import create_pool, request, extract_response_meta

from minet.defaults import (
    DEFAULT_GROUP_PARALLELISM,
    DEFAULT_GROUP_BUFFER_SIZE,
    DEFAULT_THROTTLE
)

CrawlWorkerResult = namedtuple(
    'CrawlWorkerResult',
    [
        'job',
        'items',
        'error',
        'response',
        'meta',
        'next_jobs'
    ]
)


class CrawlJob(object):
    __slots__ = ('url', 'spider')

    def __init__(self, spider, url):
        self.spider = spider
        self.url = url


class Spider(object):
    def __init__(self, definition):
        self.definition = definition
        self.start_urls = [definition['start_url']]
        self.scraper = Scraper(definition['scraper'])


def crawl(spec, queue_path=None, threads=25, buffer_size=DEFAULT_GROUP_BUFFER_SIZE,
          throttle=DEFAULT_THROTTLE):

    # Memory queue
    if queue_path is None:
        queue = Queue()

    # Persistent queue
    else:
        queue = SQLiteQueue(queue_path, auto_commit=True, multithreading=True)

    spider = Spider(spec)

    for url in spider.start_urls:
        queue.put(CrawlJob(spider, url))

    http = create_pool(
        num_pools=threads * 2,
        maxsize=1
    )

    def grouper(job):
        return get_domain_name(job.url)

    def worker(job):
        err, response = request(http, job.url)

        if err:
            return CrawlWorkerResult(
                job=job,
                items=None,
                error=err,
                response=response,
                meta=meta,
                next_jobs=None
            )

        meta = extract_response_meta(response)

        # Decoding response data
        data = response.data.decode(meta['encoding'], errors='replace')

        # Scraping items
        items = job.spider.scraper(data)

        return CrawlWorkerResult(
            job=job,
            items=items,
            error=None,
            response=response,
            meta=meta,
            next_jobs=None
        )

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
