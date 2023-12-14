# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
from minet.crowdtangle.types import CrowdTanglePost
from minet.cli.crowdtangle.utils import make_paginated_action

action = make_paginated_action(
    method_name="posts", item_name="posts", csv_headers=CrowdTanglePost.fieldnames()
)
