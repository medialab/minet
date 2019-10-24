# =============================================================================
# Minet Hyphe Dump CLI Action
# =============================================================================
#
# Logic of the `hyphe dump` action.
#
from minet.utils import create_pool
from minet.cli.hyphe.utils import create_corpus_jsonrpc

# Constants
BATCH_SIZE = 100


def hyphe_dump_action(namespace):

    # Fixing trailing slash
    if not namespace.url.endswith('/'):
        namespace.url += '/'

    http = create_pool()
    jsonrpc = create_corpus_jsonrpc(http, namespace.url, namespace.corpus)

    # First we need to start the corpus
    err, result = jsonrpc('start_corpus')

    print(result)

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
