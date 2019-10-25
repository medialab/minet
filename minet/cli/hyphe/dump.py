# =============================================================================
# Minet Hyphe Dump CLI Action
# =============================================================================
#
# Logic of the `hyphe dump` action.
#
from pprint import pprint

from minet.utils import create_pool
from minet.cli.hyphe.utils import (
    create_corpus_jsonrpc,
    ensure_corpus_is_started
)

# Constants
BATCH_SIZE = 100


# Helpers
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
    for webentity in webentities_by_status_iter(jsonrpc, 'DISCOVERED'):
        print(webentity['name'])

# {
# 	"method": "store.paginate_webentity_pages",
# 	"params": {
# 		"webentity_id": 24,
# 		"corpus": "test",
# 		"count": 10,
# 		"include_page_data": true,
# 		"onlyCrawled": true
# 	}
# }
