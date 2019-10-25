# =============================================================================
# Minet Hyphe Dump CLI Action
# =============================================================================
#
# Logic of the `hyphe dump` action.
#
from minet.utils import create_pool
from minet.cli.hyphe.utils import (
    create_corpus_jsonrpc,
    ensure_corpus_is_started
)

# Constants
BATCH_SIZE = 100


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
    err, result = jsonrpc('store.get_webentities_by_status', status='IN', count=10)

    from pprint import pprint
    pprint(result['result'])
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
