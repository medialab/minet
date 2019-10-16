# =============================================================================
# Minet Crawl
# =============================================================================
#
# Functions related to the crawling utilities of minet.
#
from queue import Queue, Empty
from persistqueue import SQLiteQueue
from quenouille import imap_unordered
from quenouille.constants import FOREVER
from ural import get_domain_name
from collections import namedtuple
from threading import Lock

from minet.scrape import Scraper
from minet.utils import (
    create_pool,
    request,
    extract_response_meta,
    PseudoFStringFormatter
)

from minet.defaults import (
    DEFAULT_GROUP_PARALLELISM,
    DEFAULT_GROUP_BUFFER_SIZE,
    DEFAULT_THROTTLE
)

FORMATTER = PseudoFStringFormatter()
TICK = 0.1

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


class ThreadSafeCounter(object):
    def __init__(self):
        self.counter = 0
        self.lock = Lock()

    def __iadd__(self, inc):
        with self.lock:
            self.counter += inc

        return self

    def __isub__(self, dec):
        with self.lock:
            self.counter -= dec

        return self

    def __eq__(self, other):
        return self.counter == other

    def __ne__(self, other):
        return self.counter != other

class CrawlJob(object):
    __slots__ = ('url', 'level')

    def __init__(self, url, level=0):
        self.url = url
        self.level = level

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s level=%(level)s url=%(url)s>'
        ) % {
            'class_name': class_name,
            'url': self.url,
            'level': self.level
        }


class Spider(object):
    def __init__(self, definition):
        self.definition = definition
        self.next_definition = definition.get('next')
        self.start_urls = [definition['start_url']]
        self.scraper = Scraper(definition['scraper'])
        self.max_level = definition.get('max_level', float('inf'))

    def get_next_jobs(self, job, html):
        if not self.next_definition:
            return

        next_level = job.level + 1

        if next_level >= self.max_level:
            return

        # Formatting next url
        if 'format' in self.next_definition:
            job = CrawlJob(
                FORMATTER.format(
                    self.next_definition['format'],
                    level=next_level
                ),
                level=next_level
            )

            return [job]


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
        queue.put((spider, CrawlJob(url)))

    http = create_pool(
        num_pools=threads * 2,
        maxsize=1
    )

    currently_working_threads = ThreadSafeCounter()
    def queue_iterator():
        nonlocal currently_working_threads

        # TODO: should not need the TICK shenaningans
        while True:
            print('Attempt')
            with currently_working_threads.lock:
                if queue.qsize() == 0 and currently_working_threads == 0:
                    break

            try:
                timeout = TICK if queue.qsize() == 0 else FOREVER
                result = queue.get(timeout=timeout)

                currently_working_threads += 1

                print('YIELDING', result)
                yield result
            except Empty:
                pass

    def grouper(payload):
        return get_domain_name(payload[1].url)

    def worker(payload):
        spider, job = payload
        print('WORKING', job)
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
        items = spider.scraper(data)

        # Finding next jobs
        next_jobs = spider.get_next_jobs(job, data)

        return CrawlWorkerResult(
            job=job,
            items=items,
            error=None,
            response=response,
            meta=meta,
            next_jobs=next_jobs
        )

    it = queue_iterator()

    print(next(it))
    queue.put('TEST')
    print(next(it))

    return

    multithreaded_iterator = imap_unordered(
        queue_iterator(),
        worker,
        threads,
        group=grouper,
        group_parallelism=DEFAULT_GROUP_PARALLELISM,
        group_buffer_size=buffer_size,
        group_throttle=throttle
    )

    for result in multithreaded_iterator:
        if result.error:
            print('Error', result.error)
            # TODO: handle error
            continue

        if result.next_jobs is not None:
            for next_job in result.next_jobs:
                queue.put((spider, next_job))

        print('DONE', result.job)

        # for item in result.items:
        #     print(item)
