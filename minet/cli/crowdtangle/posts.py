# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
from minet.crowdtangle.constants import CROWDTANGLE_POST_CSV_HEADERS
from minet.cli.crowdtangle.utils import make_paginated_action

action = make_paginated_action(
    method_name="posts", item_name="posts", csv_headers=CROWDTANGLE_POST_CSV_HEADERS
)
