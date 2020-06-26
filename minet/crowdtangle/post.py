# =============================================================================
# Minet CrowdTangle Post
# =============================================================================
#
# Function used to retrieve information per post by id.
#
from minet.crowdtangle.exceptions import (
    CrowdTangleMissingTokenError,
    CrowdTangleInvalidTokenError,
    CrowdTangleInvalidRequestError
)
from minet.utils import request_json, nested_get
from minet.crowdtangle.constants import (
    CROWDTANGLE_OUTPUT_FORMATS
)
from minet.crowdtangle.formatters import (
    format_post
)

URL_TEMPLATE = 'https://api.crowdtangle.com/post/%s?token=%s'


def crowdtangle_post(http, post_id, token=None, format='csv_dict_row'):

    if token is None:
        raise CrowdTangleMissingTokenError

    if format not in CROWDTANGLE_OUTPUT_FORMATS:
        raise TypeError('minet.crowdtangle.post: unkown `format`.')

    # Fetching
    api_url = URL_TEMPLATE % (post_id, token)

    err, response, data = request_json(http, api_url)

    if err is not None:
        raise err

    if response.status == 401:
        raise CrowdTangleInvalidTokenError

    if response.status >= 400:
        raise CrowdTangleInvalidRequestError(api_url)

    post = nested_get(['result', 'posts', 0], data)

    if post is None:
        return

    if format == 'csv_dict_row':
        return format_post(post, as_dict=True)
    elif format == 'csv_row':
        return format_post(post)

    return post
