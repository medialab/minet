# =============================================================================
# Minet CrowdTangle Leaderboard
# =============================================================================
#
# Function related to leaderboards
#
from minet.crowdtangle.utils import make_paginated_iterator
from minet.crowdtangle.formatters import format_leaderboard

URL_TEMPLATE = 'https://api.crowdtangle.com/leaderboard?count=100&token=%s'


def url_forge(token=None, list_id=None, start_date=None, **kwargs):
    base_url = URL_TEMPLATE % token

    if list_id:
        base_url += '&listId=%s' % list_id

    if start_date is not None:
        base_url += '&startDate=%s' % start_date

    return base_url


crowdtangle_leaderboard = make_paginated_iterator(
    url_forge,
    item_key='accountStatistics',
    item_id_getter=lambda x: x['account']['id'],
    formatter=format_leaderboard
)
