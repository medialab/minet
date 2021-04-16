# =============================================================================
# Minet CrowdTangle Post
# =============================================================================
#
# Function used to retrieve information per post by id.
#
from ebbe import getpath

from minet.crowdtangle.exceptions import (
    CrowdTangleMissingTokenError,
    CrowdTangleInvalidTokenError,
    CrowdTangleInvalidRequestError
)
from minet.web import request_json
from minet.crowdtangle.formatters import (
    format_post
)

URL_TEMPLATE = 'https://api.crowdtangle.com/post/%s?token=%s'


def crowdtangle_post(pool, post_id, token=None, raw=False):

    if token is None:
        raise CrowdTangleMissingTokenError

    # Fetching
    api_url = URL_TEMPLATE % (post_id, token)

    err, response, data = request_json(api_url, pool=pool)

    if err is not None:
        raise err

    if response.status == 401:
        raise CrowdTangleInvalidTokenError

    if response.status >= 400:
        raise CrowdTangleInvalidRequestError(api_url)

    post = getpath(data, ['result', 'posts', 0])

    if post is None:
        return

    if not raw:
        return format_post(post)

    return post
