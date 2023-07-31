import time
from quenouille import imap_unordered
from minet.crawl.types import CrawlJob
from minet.crawl.queue import CrawlerQueue
from minet.cli.console import console


def worker(job: CrawlJob) -> CrawlJob:
    time.sleep(1)
    return job


queue = CrawlerQueue()

jobs = [CrawlJob("1", group="A"), CrawlJob("2", group="A"), CrawlJob("3", group="A")]
queue.put_many(jobs)

for job in imap_unordered(queue, worker, 3, buffer_size=0):
    console.print(job, highlight=True)
    queue.task_done(job)
