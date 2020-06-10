# =============================================================================
# Minet Twitter Friends CLI Action
# =============================================================================
#
# Logic of the `tw followers` action.
#
from minet.cli.twitter.utils import make_twitter_action

REPORT_HEADERS = [
    'followers_id'
]

twitter_followers_action = make_twitter_action(
    method_name='followers',
    csv_headers=REPORT_HEADERS
)
