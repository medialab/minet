import casanova
from os.path import isdir

from minet.crawl.queue import CrawlerQueue, CrawlerQueueRecord

from minet.cli.exceptions import FatalError


def action(cli_args):
    if not isdir(cli_args.queue_dir):
        raise FatalError("queue does not exist")

    queue = CrawlerQueue(cli_args.queue_dir, inspect=True)

    writer = casanova.writer(
        cli_args.output, fieldnames=CrawlerQueueRecord.fieldnames()
    )

    for record in queue.dump():
        writer.writerow(record)
