# =============================================================================
# Minet Hyphe Dump CLI Action
# =============================================================================
#
# Logic of the `hyphe dump` action.
#
from tqdm import tqdm

from minet.utils import create_pool
from minet.cli.hyphe.constants import WEBENTITY_STATUSES
from minet.cli.hyphe.utils import (
    create_corpus_jsonrpc,
    ensure_corpus_is_started
)

# Constants
BATCH_SIZE = 100


# Helpers
def count_total_webentities(stats, statuses=WEBENTITY_STATUSES):
    counts = stats['result']['corpus']['traph']['webentities']

    total = 0

    for status in statuses:
        total += counts[status]

    return total


def count_total_pages(stats):
    counts = stats['result']['corpus']['crawler']

    return counts['pages_found']


def webentities_by_status_iter(jsonrpc, status):
    token = None
    next_page = None

    while True:
        if token is None:
            err, result = jsonrpc(
                'store.get_webentities_by_status',
                status=status,
                count=BATCH_SIZE
            )
        else:
            err, result = jsonrpc(
                'store.get_webentities_page',
                pagination_token=token,
                n_page=next_page
            )

        result = result['result']

        for webentity in result['webentities']:
            yield webentity

        if 'next_page' in result and result['next_page']:
            token = result['token']
            next_page = result['next_page']
        else:
            break


def webentities_iter(jsonrpc, statuses=WEBENTITY_STATUSES):
    for status in statuses:
        yield from webentities_by_status_iter(jsonrpc, status)


def webentity_pages_iter(jsonrpc, webentity_id):
    token = None

    while True:
        err, result = jsonrpc(
            'store.paginate_webentity_pages',
            webentity_id=webentity_id,
            count=BATCH_SIZE,
            pagination_token=token
        )

        result = result['result']

        for page in result['pages']:
            yield page

        if 'token' in result and result['token']:
            token = result['token']
        else:
            break


def pages_iter(jsonrpc, webentities):
    for webentity in webentities.values():
        yield from webentity_pages_iter(jsonrpc, webentity['id'])


def hyphe_dump_action(namespace):

    # Fixing trailing slash
    if not namespace.url.endswith('/'):
        namespace.url += '/'

    http = create_pool()
    jsonrpc = create_corpus_jsonrpc(http, namespace.url, namespace.corpus)

    # First we need to start the corpus
    ensure_corpus_is_started(jsonrpc)

    # Then we gather some handy statistics
    err, stats = jsonrpc('get_status')

    # Then we fetch webentities
    loading_bar = tqdm(
        desc='Paginating web entities',
        unit=' webentities',
        dynamic_ncols=True,
        total=count_total_webentities(stats)
    )

    webentities = {}

    for webentity in webentities_iter(jsonrpc):
        loading_bar.update()
        webentities[webentity['id']] = webentity

    loading_bar.close()

    # Finally we paginate pages
    loading_bar = tqdm(
        desc='Dumping pages',
        unit=' pages',
        dynamic_ncols=True,
        total=count_total_pages(stats)
    )

    for page in pages_iter(jsonrpc, webentities):
        loading_bar.update()
