import casanova
from os.path import isdir

from minet.crawl.queue import CrawlerQueue

from minet.cli.exceptions import FatalError


def action(cli_args):
    if not isdir(cli_args.queue_dir):
        raise FatalError("queue does not exist")

    queue = CrawlerQueue(cli_args.queue_dir, resume=True)

    writer = casanova.writer(cli_args.output, fieldnames=["status", "depth", "url"])

    for status, job in queue.dump():
        writer.writerow([status, job.depth, job.url])
