# =============================================================================
# Minet CrowdTangle Search CLI Action
# =============================================================================
#
# Logic of the `ct search` action.
#
from minet.crowdtangle.types import CrowdTanglePost
from minet.cli.crowdtangle.utils import make_paginated_action

action = make_paginated_action(
    method_name="search",
    item_name="posts",
    csv_headers=CrowdTanglePost.fieldnames(),
    get_args=lambda cli_args: [cli_args.terms],
    announce=lambda cli_args: 'Searching for: "%s"' % cli_args.terms,
)
