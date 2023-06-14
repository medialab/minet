import casanova
from os.path import isdir

from minet.crawl.url_cache import URLCache

from minet.cli.exceptions import FatalError


def action(cli_args):
    if not isdir(cli_args.urls_dir):
        raise FatalError("queue does not exist")

    # NOTE: we are only dumping so we don't need to indicate that
    # the store is normalized or not.
    store = URLCache(cli_args.urls_dir)

    writer = casanova.writer(cli_args.output, fieldnames=["url"])

    for url in store:
        writer.writerow([url])
