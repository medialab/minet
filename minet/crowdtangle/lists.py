# =============================================================================
# Minet CrowdTangle Lists
# =============================================================================
#
# Function used to retrieved lists from a given dashboard.
#
from minet.crowdtangle.exceptions import CrowdTangleMissingTokenError
from minet.crowdtangle.formatters import format_list

URL_TEMPLATE = "https://api.crowdtangle.com/lists?token=%s"


def crowdtangle_lists(request, token=None, raw=False):

    if token is None:
        raise CrowdTangleMissingTokenError

    # Fetching
    api_url = URL_TEMPLATE % token

    data = request(api_url)
    lists = data["lists"]

    if not raw:
        return [format_list(l) for l in lists]

    return lists
