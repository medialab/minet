# =============================================================================
# Minet CrowdTangle Search CLI Action
# =============================================================================
#
# Logic of the `ct search` action.
#
from minet.crowdtangle.constants import CROWDTANGLE_POST_CSV_HEADERS
from minet.cli.crowdtangle.utils import make_paginated_action

crowdtangle_search_action = make_paginated_action(
    method_name='search',
    item_name='posts',
    csv_headers=CROWDTANGLE_POST_CSV_HEADERS,
    get_args=lambda namespace: [namespace.terms]
)
