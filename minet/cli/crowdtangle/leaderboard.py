# =============================================================================
# Minet CrowdTangle Leaderboard CLI Action
# =============================================================================
#
# Logic of the `ct leaderboard` action.
#
from minet.crowdtangle.types import CrowdTangleLeaderboard
from minet.cli.crowdtangle.utils import make_paginated_action


action = make_paginated_action(
    method_name="leaderboard",
    item_name="accounts",
    csv_headers=CrowdTangleLeaderboard.fieldnames(),
)
