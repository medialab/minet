# =============================================================================
# Minet CrowdTangle Lists
# =============================================================================
#
# Function used to retrieved lists from a given dashboard.
#
from ebbe import getpath

from minet.crowdtangle.exceptions import (
    CrowdTangleMissingTokenError,
    CrowdTangleInvalidTokenError,
    CrowdTangleInvalidRequestError
)
from minet.web import request_json
from minet.crowdtangle.formatters import (
    format_list
)

URL_TEMPLATE = 'https://api.crowdtangle.com/lists?token=%s'


def crowdtangle_lists(pool, token=None, raw=False):

    if token is None:
        raise CrowdTangleMissingTokenError

    # Fetching
    api_url = URL_TEMPLATE % token

    err, response, data = request_json(api_url, pool=pool)

    if err is not None:
        raise err

    if response.status == 401:
        raise CrowdTangleInvalidTokenError

    if response.status >= 400:
        raise CrowdTangleInvalidRequestError(api_url)

    lists = getpath(data, ['result', 'lists'])

    if not raw:
        return [format_list(l) for l in lists]

    return lists
