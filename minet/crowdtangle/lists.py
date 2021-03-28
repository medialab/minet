# =============================================================================
# Minet CrowdTangle Lists
# =============================================================================
#
# Function used to retrieved lists from a given dashboard.
#
from minet.crowdtangle.exceptions import (
    CrowdTangleMissingTokenError,
    CrowdTangleInvalidTokenError,
    CrowdTangleInvalidRequestError
)
from minet.utils import nested_get
from minet.web import request_json
from minet.crowdtangle.constants import (
    CROWDTANGLE_OUTPUT_FORMATS
)
from minet.crowdtangle.formatters import (
    format_list
)

URL_TEMPLATE = 'https://api.crowdtangle.com/lists?token=%s'


def crowdtangle_lists(pool, token=None, format='csv_dict_row'):

    if token is None:
        raise CrowdTangleMissingTokenError

    if format not in CROWDTANGLE_OUTPUT_FORMATS:
        raise TypeError('minet.crowdtangle.lists: unkown `format`.')

    # Fetching
    api_url = URL_TEMPLATE % token

    err, response, data = request_json(api_url, pool=pool)

    if err is not None:
        raise err

    if response.status == 401:
        raise CrowdTangleInvalidTokenError

    if response.status >= 400:
        raise CrowdTangleInvalidRequestError(api_url)

    lists = nested_get(['result', 'lists'], data)

    if format == 'csv_dict_row':
        return [format_list(l, as_dict=True) for l in lists]
    elif format == 'csv_row':
        return [format_list(l) for l in lists]

    return lists
