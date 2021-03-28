# =============================================================================
# Minet Crawl
# =============================================================================
#
# Functions related to the crawling utilities of minet.
#
from queue import Queue
from persistqueue import SQLiteQueue
from quenouille import imap_unordered, QueueIterator
from bs4 import BeautifulSoup
from ural import get_domain_name
from collections import namedtuple
from urllib.parse import urljoin
from shutil import rmtree
from threading import Lock

from minet.scrape import Scraper
from minet.utils import load_definition
from minet.web import (
    create_pool,
    request,
    extract_response_meta
)
from minet.utils import PseudoFStringFormatter

from minet.exceptions import UnknownSpiderError

from minet.constants import (
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
        'content',
        'next_jobs'
    ]
)


def ensure_list(value):
    if not isinstance(value, list):
        return [value]
    return value


class CrawlJob(object):
    __slots__ = ('url', 'level', 'spider', 'data')

    def __init__(self, url, level=0, spider='default', data=None):
        self.url = url
        self.level = level
        self.spider = spider
        self.data = data

    def id(self):
        return '%x' % id(self)

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


def ensure_job(url_or_job):
    if isinstance(url_or_job, CrawlJob):
        return url_or_job

    return CrawlJob(url=url_or_job)


class CrawlerState(object):
    def __init__(self):
        self.__lock = Lock()

        self.jobs_done = 0
        self.jobs_doing = 0
        self.jobs_queued = 0

    def inc_queued(self):
        with self.__lock:
            self.jobs_queued += 1

    def dec_queued(self):
        with self.__lock:
            self.jobs_queued -= 1

    def inc_done(self):
        with self.__lock:
            self.jobs_done += 1

    def inc_doing(self):
        with self.__lock:
            self.jobs_doing += 1

    def dec_doing(self):
        with self.__lock:
            self.jobs_doing -= 1

    def inc_working(self):
        with self.__lock:
            self.jobs_queued -= 1
            self.jobs_doing += 1

    def dec_working(self):
        with self.__lock:
            self.jobs_done += 1
            self.jobs_doing -= 1

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s queued=%(jobs_queued)i doing=%(jobs_doing)i done=%(jobs_done)i>'
        ) % {
            'class_name': class_name,
            'jobs_done': self.jobs_done,
            'jobs_queued': self.jobs_queued,
            'jobs_doing': self.jobs_doing
        }


class Spider(object):
    def __init__(self, name='default'):
        self.name = name

    def start_jobs(self):
        return None

    def extract_meta_from_response(self, job, response):
        return extract_response_meta(response)

    def process_content(self, job, response, meta=None):
        return response.data.decode(meta['encoding'], errors='replace')

    def scrape(self, job, response, content, meta=None):
        return None

    def next_jobs(self, job, response, content, meta=None):
        return None

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s name=%(name)s>'
        ) % {
            'class_name': class_name,
            'name': self.name
        }


class FunctionSpider(Spider):
    def __init__(self, fn, name='default'):
        super().__init__(name)
        self.fn = fn

    def process(self, job, response, content, meta=None):
        return self.fn(job, response, content, meta)


class BeautifulSoupSpider(Spider):
    def __init__(self, name='default', engine='lxml'):
        super().__init__(name)
        self.engine = engine

    def process_content(self, job, response, meta=None):
        decoded_content = super().process_content(job, response, meta)

        soup = BeautifulSoup(decoded_content, self.engine)

        return soup


class DefinitionSpider(Spider):
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
        self.next_scrapers = {}

        if 'scraper' in definition:
            self.scraper = Scraper(definition['scraper'])

        if 'scrapers' in definition:
            for name, scraper in definition['scrapers'].items():
                self.scrapers[name] = Scraper(scraper)

        if self.next_definition is not None:
            if 'scraper' in self.next_definition:
                self.next_scraper = Scraper(self.next_definition['scraper'])

            if 'scrapers' in self.next_definition:
                for name, scraper in self.next_definition['scrapers'].items():
                    self.next_scrapers[name] = Scraper(scraper)

    def start_jobs(self):

        # TODO: possibility to name this as jobs
        start_urls = (
            ensure_list(self.definition.get('start_url', [])) +
            ensure_list(self.definition.get('start_urls', []))
        )

        for url in start_urls:
            yield CrawlJob(url, spider=self.name)

    def next_targets(self, content, next_level):

        # Scraping next results
        if self.next_scraper is not None:
            scraped = self.next_scraper(content)

            if scraped is not None:
                if isinstance(scraped, list):
                    yield from scraped
                else:
                    yield scraped

        if self.next_scrapers:
            for scraper in self.next_scrapers.values():
                scraped = scraper(content)

                if scraped is not None:
                    if isinstance(scraped, list):
                        yield from scraped
                    else:
                        yield scraped

        # Formatting next url
        if 'format' in self.next_definition:
            yield FORMATTER.format(
                self.next_definition['format'],
                level=next_level
            )

    def job_from_target(self, current_url, target, next_level):
        if isinstance(target, str):
            return CrawlJob(
                url=urljoin(current_url, target),
                spider=self.name,
                level=next_level
            )

        else:

            # TODO: validate target
            return CrawlJob(
                url=urljoin(current_url, target['url']),
                spider=target.get('spider', self.name),
                level=next_level,
                data=target.get('data')
            )

    def next_jobs(self, job, response, content, meta=None):
        if not self.next_definition:
            return

        next_level = job.level + 1

        if next_level > self.max_level:
            return

        for target in self.next_targets(content, next_level):
            yield self.job_from_target(response.geturl(), target, next_level)

    def scrape(self, job, response, content, meta=None):
        scraped = {
            'single': None,
            'multiple': {}
        }

        context = {'job': job.id(), 'url': job.url}

        if self.scraper is not None:
            scraped['single'] = self.scraper(content, context=context)

        for name, scraper in self.scrapers.items():
            scraped['multiple'][name] = scraper(content, context=context)

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

    # TODO: start_jobs with multiple spiders
    def __init__(self, spec=None, spider=None, spiders=None, start_jobs=None,
                 queue_path=None, threads=25,
                 buffer_size=DEFAULT_GROUP_BUFFER_SIZE, throttle=DEFAULT_THROTTLE):

        # NOTE: crawling could work depth-first but:
        # buffer_size should be 0 (requires to fix quenouille issue #1)

        # Params
        self.start_jobs = start_jobs
        self.queue_path = queue_path
        self.threads = threads
        self.buffer_size = buffer_size
        self.throttle = throttle

        self.using_persistent_queue = queue_path is not None
        self.pool = create_pool(threads=threads)
        self.state = CrawlerState()
        self.started = False

        # Memory queue
        if not self.using_persistent_queue:
            queue = Queue()

        # Persistent queue
        else:
            queue = SQLiteQueue(queue_path, multithreading=True, auto_commit=False)

        # Creating spiders
        if spec is not None:
            if not isinstance(spec, dict):
                spec = load_definition(spec)

            if 'spiders' in spec:
                spiders = {name: DefinitionSpider(s, name=name) for name, s in spec['spiders'].items()}
                self.single_spider = False
            else:
                spiders = {'default': DefinitionSpider(spec)}
                self.single_spider = True

        elif spider is not None:
            spiders = {'default': spider}

        elif spiders is None:
            raise TypeError('minet.Crawler: expecting either `spec`, `spider` or `spiders`.')

        # Solving function spiders
        for name, s in spiders.items():
            if callable(s) and not isinstance(s, Spider):
                spiders[name] = FunctionSpider(s, name)

        self.queue = queue
        self.spiders = spiders

    def enqueue(self, job_or_jobs):
        if not isinstance(job_or_jobs, (CrawlJob, str)):
            for job in job_or_jobs:
                assert isinstance(job, (CrawlJob, str))
                self.queue.put(ensure_job(job))
                self.state.inc_queued()
        else:
            self.queue.put(ensure_job(job_or_jobs))
            self.state.inc_queued()

    def start(self):

        if self.started:
            return

        # Collecting start jobs - we only add those if queue is not pre-existing
        if self.queue.qsize() == 0:

            # NOTE: start jobs are all buffered into memory
            # We could use a blocking queue with max size but this could prove
            # difficult to resume crawls based upon lazy iterators
            if self.start_jobs:
                self.enqueue(self.start_jobs)

            for spider in self.spiders.values():
                spider_start_jobs = spider.start_jobs()

                if spider_start_jobs is not None:
                    self.enqueue(spider_start_jobs)

        self.started = True

    def work(self, job):
        self.state.inc_working()

        spider = self.spiders.get(job.spider)

        if spider is None:
            raise UnknownSpiderError('Unknown spider "%s"' % job.spider)

        err, response = request(job.url, pool=self.pool)

        if err:
            return CrawlWorkerResult(
                job=job,
                scraped=None,
                error=err,
                response=response,
                meta=None,
                content=None,
                next_jobs=None
            )

        meta = spider.extract_meta_from_response(job, response)

        # Decoding response content
        content = spider.process_content(job, response, meta)

        if isinstance(spider, FunctionSpider):
            scraped, next_jobs = spider.process(job, response, content, meta)
        else:

            # Scraping items
            scraped = spider.scrape(job, response, content, meta)

            # Finding next jobs
            next_jobs = spider.next_jobs(job, response, content, meta)

        # Enqueuing next jobs
        if next_jobs is not None:

            # Consuming so that multiple agents may act on this
            next_jobs = list(next_jobs)
            self.enqueue(next_jobs)

        self.state.dec_working()

        return CrawlWorkerResult(
            job=job,
            scraped=scraped,
            error=None,
            response=response,
            meta=meta,
            content=content,
            next_jobs=next_jobs
        )

    def __iter__(self):

        self.start()

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
                    yield result

            self.cleanup()

        return generator()

    def cleanup(self):

        # Releasing queue (needed by persistqueue)
        if self.using_persistent_queue:
            del self.queue
            rmtree(self.queue_path, ignore_errors=True)
