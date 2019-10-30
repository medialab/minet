# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
import os

from minet.crawl import Crawler
from minet.utils import load_definition


def crawl_action(namespace):

    # Scaffolding output directory
    os.makedirs(namespace.output_dir, exist_ok=True)

    # Loading crawler definition
    definition = load_definition(namespace.crawler)

    crawler = Crawler(definition, throttle=namespace.throttle)
