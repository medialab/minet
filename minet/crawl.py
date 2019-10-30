# =============================================================================
# Minet Crawl
# =============================================================================
#
# Functions related to the crawling utilities of minet.
#
from queue import Queue
from persistqueue import SQLiteQueue
from quenouille import imap_unordered, QueueIterator
from ural import get_domain_name
from collections import namedtuple
from urllib.parse import urljoin
from shutil import rmtree

from minet.scrape import Scraper
from minet.utils import (
    create_pool,
    request,
    extract_response_meta,
    PseudoFStringFormatter
)

from minet.exceptions import UnknownSpiderError

from minet.defaults import (
    DEFAULT_GROUP_PARALLELISM,
    DEFAULT_GROUP_BUFFER_SIZE,
    DEFAULT_THROTTLE
)

FORMATTER = PseudoFStringFormatter()

CrawlWorkerResult = namedtuple(
    'CrawlWorkerResult',
    [
        'job',
        'scraped',
        'error',
        'response',
        'meta',
        'next_jobs'
    ]
)


def ensure_list(value):
    if not isinstance(value, list):
        return [value]
    return value


class CrawlJob(object):
    __slots__ = ('url', 'level', 'spider')

    def __init__(self, url, level=0, spider='default'):
        self.url = url
        self.level = level
        self.spider = spider

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s level=%(level)s url=%(url)s spider=%(spider)s>'
        ) % {
            'class_name': class_name,
            'url': self.url,
            'level': self.level,
            'spider': self.spider
        }

    @staticmethod
    def grouper(job):
        return get_domain_name(job.url)


class CrawlerState(object):
    __slots__ = ('jobs_done', 'jobs_queued')

    def __init__(self):
        self.jobs_done = 0
        self.jobs_queued = 0

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s done=%(jobs_done)s queued=%(jobs_queued)s>'
        ) % {
            'class_name': class_name,
            'jobs_done': self.jobs_done,
            'jobs_queued': self.jobs_queued
        }


class Spider(object):
    def __init__(self, definition, name='default'):

        # Descriptors
        self.name = name
        self.definition = definition
        self.next_definition = definition.get('next')

        # Settings
        self.max_level = definition.get('max_level', float('inf'))

        # Scrapers
        self.scraper = None
        self.scrapers = {}
        self.next_scraper = None

        if 'scraper' in definition:
            self.scraper = Scraper(definition['scraper'])

        if 'scrapers' in definition:
            for name, scraper in definition['scrapers'].items():
                self.scrapers[name] = Scraper(scraper)

        if self.next_definition is not None and 'scraper' in self.next_definition:
            self.next_scraper = Scraper(self.next_definition['scraper'])

    def get_start_jobs(self):
        start_urls = (
            ensure_list(self.definition.get('start_url', [])) +
            ensure_list(self.definition.get('start_urls', []))
        )

        return [CrawlJob(url, spider=self.name) for url in start_urls]

    def job_from_target(self, target, current_url, next_level):
        if isinstance(target, str):
            return CrawlJob(
                url=urljoin(current_url, target),
                level=next_level,
                spider=self.name
            )

        # TODO: validate target
        return CrawlJob(
            url=urljoin(current_url, target['url']),
            level=next_level,
            spider=target.get('spider', self.name)
        )

    def next_targets_iter(self, job, html):
        next_level = job.level + 1

        # Scraping next results
        if self.next_scraper is not None:
            scraped = self.next_scraper(html)

            if isinstance(scraped, list):
                yield from scraped
            else:
                yield scraped

        # Formatting next url
        elif 'format' in self.next_definition:
            yield FORMATTER.format(
                self.next_definition['format'],
                level=next_level
            )

    def get_next_jobs(self, job, html, current_url):
        if not self.next_definition:
            return

        next_level = job.level + 1

        if next_level > self.max_level:
            return

        next_jobs = []

        for target in self.next_targets_iter(job, html):
            next_jobs.append(self.job_from_target(target, current_url, next_level))

        return next_jobs

    def scrape(self, response_data):
        scraped = {
            'single': None,
            'multiple': {}
        }

        if self.scraper is not None:
            scraped['single'] = self.scraper(response_data)

        for name, scraper in self.scrapers.items():
            scraped['multiple'][name] = scraper(response_data)

        return scraped


class TaskContext(object):
    def __init__(self, queue, queue_iterator):
        self.queue = queue
        self.queue_iterator = queue_iterator

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.queue.task_done()
        self.queue_iterator.task_done()


class Crawler(object):
    def __init__(self, spec, queue_path=None, threads=25,
                 buffer_size=DEFAULT_GROUP_BUFFER_SIZE, throttle=DEFAULT_THROTTLE):

        # NOTE: crawling could work depth-first but:
        # buffer_size should be 0 (requires to fix quenouille issue #1)

        # Params
        self.queue_path = queue_path
        self.threads = threads
        self.buffer_size = buffer_size
        self.throttle = throttle

        self.using_persistent_queue = queue_path is not None
        self.http = create_pool(threads=threads)

        # Memory queue
        if not self.using_persistent_queue:
            queue = Queue()

        # Persistent queue
        else:
            queue = SQLiteQueue(queue_path, multithreading=True, auto_commit=False)

        # Creating spiders
        if 'spiders' in spec:
            spiders = {name: Spider(s, name=name) for name, s in spec['spiders'].items()}
        else:
            spiders = {'default': Spider(spec)}

        self.queue = queue
        self.spiders = spiders

    def enqueue(self, jobs):
        for job in jobs:
            assert type(job) is CrawlJob
            self.queue.put(job)

    def start(self):

        # Collecting start jobs - we only add those if queue is not pre-existing
        if self.queue.qsize() == 0:
            for spider in self.spiders.values():
                self.enqueue(spider.get_start_jobs())

    def work(self, job):
        spider = self.spiders.get(job.spider)

        if spider is None:
            raise UnknownSpiderError('Unknown spider "%s"' % job.spider)

        err, response = request(self.http, job.url)

        if err:
            return CrawlWorkerResult(
                job=job,
                scraped=None,
                error=err,
                response=response,
                meta=None,
                next_jobs=None
            )

        meta = extract_response_meta(response)

        # Decoding response data
        data = response.data.decode(meta['encoding'], errors='replace')

        # Scraping items
        scraped = spider.scrape(data)

        # Finding next jobs
        next_jobs = spider.get_next_jobs(job, data, response.geturl())

        return CrawlWorkerResult(
            job=job,
            scraped=scraped,
            error=None,
            response=response,
            meta=meta,
            next_jobs=next_jobs
        )

    def __iter__(self):
        queue_iterator = QueueIterator(self.queue)
        task_context = TaskContext(self.queue, queue_iterator)

        multithreaded_iterator = imap_unordered(
            queue_iterator,
            self.work,
            self.threads,
            group=CrawlJob.grouper,
            group_parallelism=DEFAULT_GROUP_PARALLELISM,
            group_buffer_size=self.buffer_size,
            group_throttle=self.throttle
        )

        def generator():
            for result in multithreaded_iterator:
                with task_context:

                    # Errored job
                    if result.error:
                        yield result

                        continue

                    # Enqueuing next jobs
                    # TODO: enqueueing should also be done in worker
                    if result.next_jobs is not None:
                        self.enqueue(result.next_jobs)

                    yield result

            self.cleanup()

        return generator()

    def cleanup(self):

        # Releasing queue (needed by persistqueue)
        if self.using_persistent_queue:
            del self.queue
            rmtree(self.queue_path)


def crawl(spec, queue_path=None, threads=25, buffer_size=DEFAULT_GROUP_BUFFER_SIZE,
          throttle=DEFAULT_THROTTLE):

    crawler = Crawler(
        spec,
        queue_path=queue_path,
        threads=threads,
        buffer_size=buffer_size,
        throttle=throttle
    )

    crawler.start()

    yield from crawler
