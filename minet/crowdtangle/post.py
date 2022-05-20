# =============================================================================
# Minet CrowdTangle Post
# =============================================================================
#
# Function used to retrieve information per post by id.
#
from ebbe import getpath

from minet.crowdtangle.exceptions import CrowdTangleMissingTokenError
from minet.crowdtangle.formatters import format_post

URL_TEMPLATE = "https://api.crowdtangle.com/post/%s?token=%s"


def crowdtangle_post(request, post_id, token=None, raw=False):

    if token is None:
        raise CrowdTangleMissingTokenError

    # Fetching
    api_url = URL_TEMPLATE % (post_id, token)
    data = request(api_url)
    post = getpath(data, ["posts", 0])

    if post is None:
        return

    if not raw:
        return format_post(post)

    return post
