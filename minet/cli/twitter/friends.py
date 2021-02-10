# =============================================================================
# Minet Twitter Friends CLI Action
# =============================================================================
#
# Logic of the `tw friends` action.
#
from minet.cli.twitter.utils import make_twitter_action

REPORT_HEADERS = [
    'friend_id'
]

twitter_friends_action = make_twitter_action(
    method_name='friends',
    csv_headers=REPORT_HEADERS
)
