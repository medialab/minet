# =============================================================================
# Minet Hyphe Dump CLI Action
# =============================================================================
#
# Logic of the `hyphe dump` action.
#
from minet.utils import create_pool, jsonrpc


def hyphe_dump_action(namespace):

    # Fixing trailing slash
    if not namespace.url.endswith('/'):
        namespace.url += '/'

    http = create_pool()

    def hyphe_jsonrpc(method, *args, **kwargs):
        err, jsonrpc_result = jsonrpc(http, namespace.url, method, *args, **kwargs)

        if err:
            return err, None

        return None, jsonrpc_result[0]

    err, data = hyphe_jsonrpc('get_status')

    print(err, data)
