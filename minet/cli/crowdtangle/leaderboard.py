# =============================================================================
# Minet CrowdTangle Leaderboard CLI Action
# =============================================================================
#
# Logic of the `ct leaderboard` action.
#
from minet.crowdtangle.constants import (
    CROWDTANGLE_LEADERBOARD_CSV_HEADERS,
    CROWDTANGLE_LEADERBOARD_CSV_HEADERS_WITH_BREAKDOWN
)
from minet.cli.crowdtangle.utils import make_paginated_action


def select_csv_headers(namespace):
    if namespace.breakdown:
        return CROWDTANGLE_LEADERBOARD_CSV_HEADERS_WITH_BREAKDOWN

    return CROWDTANGLE_LEADERBOARD_CSV_HEADERS


crowdtangle_leaderboard_action = make_paginated_action(
    method_name='leaderboard',
    item_name='accounts',
    csv_headers=select_csv_headers
)
