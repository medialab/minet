# =============================================================================
# Minet CrowdTangle Search CLI Action
# =============================================================================
#
# Logic of the `ct search` action.
#
from urllib.parse import quote

from minet.cli.crowdtangle.utils import create_paginated_action
from minet.cli.crowdtangle.posts import CSV_HEADERS, format_post_for_csv

URL_TEMPLATE = 'https://api.crowdtangle.com/posts/search?count=100&sortBy=%(sort_by)s&token=%(token)s&searchTerm=%(terms)s'


def forge_posts_url(namespace):
    base_url = URL_TEMPLATE % {
        'sort_by': namespace.sort_by,
        'token': namespace.token,
        'terms': quote(namespace.terms)
    }

    if namespace.start_date:
        base_url += '&startDate=%s' % namespace.start_date

    if namespace.end_date:
        base_url += '&endDate=%s' % namespace.end_date

    if namespace.platforms:
        base_url += '&platforms=%s' % namespace.platforms

    if namespace.types:
        base_url += '&types=%s' % namespace.types

    if namespace.offset:
        base_url += '&offset=%s' % namespace.offset

    if namespace.not_in_title:
        base_url += '&notInTitle'

    return base_url


crowdtangle_search_action = create_paginated_action(
    url_forge=forge_posts_url,
    csv_headers=CSV_HEADERS,
    csv_formatter=format_post_for_csv,
    item_name='posts',
    item_key='posts'
)
