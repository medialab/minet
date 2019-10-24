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

        return None, jsonrpc_result[0]

    return hyphe_jsonrpc
