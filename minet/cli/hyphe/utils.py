# =============================================================================
# Minet Hyphe CLI Utils
# =============================================================================
#
# Miscellaneous helper functions related to Hyphe API.
#
from minet.utils import jsonrpc


def create_corpus_jsonrpc(http, url, corpus):
    def hyphe_jsonrpc(method, *args, **kwargs):
        err, jsonrpc_result = jsonrpc(http, url, method, corpus=corpus, **kwargs)

        if err:
            return err, None

        if 'fault' in jsonrpc_result:
            return jsonrpc_result, None

        return None, jsonrpc_result[0]

    return hyphe_jsonrpc


def ensure_corpus_is_started(corpus_jsonrpc):
    err, result = corpus_jsonrpc('start_corpus')

    if err:
        raise err

    if result['result']['status'] == 'ready':
        return True

    # Pinging until ready
    for _ in range(10):
        err, result = corpus_jsonrpc('ping', timeout=5)

        if result['result'] == 'pong':
            return True

    raise Exception('Could not start Hyphe corpus')
