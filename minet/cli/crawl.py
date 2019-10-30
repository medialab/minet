# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
import os
from os.path import join
from tqdm import tqdm

from minet.crawl import Crawler
from minet.utils import load_definition


def crawl_action(namespace):

    # Scaffolding output directory
    os.makedirs(namespace.output_dir, exist_ok=True)

    queue_path = None

    if namespace.persist_queue:
        queue_path = join(namespace.output_dir, 'queue')

    # Loading crawler definition
    definition = load_definition(namespace.crawler)

    crawler = Crawler(
        definition,
        throttle=namespace.throttle,
        queue_path=queue_path
    )
