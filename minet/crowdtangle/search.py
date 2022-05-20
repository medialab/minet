# =============================================================================
# Minet CrowdTangle Search
# =============================================================================
#
# Function related to post search.
#
from urllib.parse import quote

from minet.crowdtangle.utils import make_paginated_iterator
from minet.crowdtangle.formatters import format_post

URL_TEMPLATE = "https://api.crowdtangle.com/posts/search?count=100&sortBy=%(sort_by)s&token=%(token)s&searchTerm=%(terms)s"


def url_forge(**kwargs):
    base_url = URL_TEMPLATE % {
        "sort_by": kwargs["sort_by"],
        "token": kwargs["token"],
        "terms": quote(kwargs["terms"]),
    }

    if kwargs.get("start_date") is not None:
        base_url += "&startDate=%s" % kwargs["start_date"]

    if kwargs.get("end_date") is not None:
        base_url += "&endDate=%s" % kwargs["end_date"]

    if kwargs.get("platforms") is not None:
        base_url += "&platforms=%s" % ",".join(kwargs["platforms"])

    if kwargs.get("types") is not None:
        base_url += "&types=%s" % ",".join(kwargs["types"])

    if kwargs.get("offset") is not None:
        base_url += "&offset=%s" % kwargs["offset"]

    if kwargs.get("not_in_title") is not None:
        base_url += "&notInTitle"

    if kwargs.get("and") is not None:
        base_url += "&and=%s" % quote(kwargs["and"])

    if kwargs.get("language") is not None:
        base_url += "&language=%s" % kwargs["language"]

    if kwargs.get("search_field") is not None:
        base_url += "&searchField=%s" % kwargs["search_field"]

    if kwargs.get("in_list_ids") is not None:
        base_url += "&inListIds=%s" % (",".join(kwargs["in_list_ids"]))

    return base_url


crowdtangle_search = make_paginated_iterator(
    url_forge, item_key="posts", formatter=format_post
)
