# =============================================================================
# Minet CrowdTangle Posts
# =============================================================================
#
# Function related to posts fetching.
#
from minet.crowdtangle.utils import make_paginated_iterator
from minet.crowdtangle.formatters import format_post

URL_TEMPLATE = (
    "https://api.crowdtangle.com/posts?count=100&sortBy=%(sort_by)s&token=%(token)s"
)


def url_forge(
    token=None,
    sort_by=None,
    language=None,
    start_date=None,
    end_date=None,
    list_ids=None,
    **kwargs
):
    base_url = URL_TEMPLATE % {"sort_by": sort_by, "token": token}

    if language:
        base_url += "&language=%s" % language

    if start_date:
        base_url += "&startDate=%s" % start_date

    if end_date:
        base_url += "&endDate=%s" % end_date

    if list_ids:
        base_url += "&listIds=%s" % ",".join(list_ids)

    return base_url


crowdtangle_posts = make_paginated_iterator(
    url_forge, item_key="posts", formatter=format_post
)
