# =============================================================================
# Minet CrowdTangle Search CLI Action
# =============================================================================
#
# Logic of the `ct search` action.
#
import json

from minet.cli.crowdtangle.utils import create_paginated_action
from minet.cli.crowdtangle.posts import CSV_HEADERS, format_post_for_csv

URL_TEMPLATE = 'https://api.crowdtangle.com/posts/search?count=100&sortBy=%(sort_by)s&token=%(token)s&searchTerm=%(terms)s'


def forge_posts_url(namespace):
    base_url = URL_TEMPLATE % {
        'sort_by': namespace.sort_by,
        'token': namespace.token,
        'terms': namespace.terms
    }

    if namespace.start_date:
        base_url += '&startDate=%s' % namespace.start_date

    if namespace.end_date:
        base_url += '&endDate=%s' % namespace.end_date

    return base_url


crowdtangle_search_action = create_paginated_action(
    url_forge=forge_posts_url,
    csv_headers=CSV_HEADERS,
    csv_formatter=format_post_for_csv,
    item_name='posts',
    item_key='posts'
)
