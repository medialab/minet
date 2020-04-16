# =============================================================================
# Minet CrowdTangle Links Summary
# =============================================================================
#
# Function related to link summary using CrowdTangle's APIs.
#
from urllib.parse import quote

from minet.crowdtangle.exceptions import CrowdTangleMissingTokenError
from minet.utils import create_pool, request_json, RateLimiter, nested_get

from minet.crowdtangle.constants import (
    CROWDTANTLE_LINKS_DEFAULT_RATE_LIMIT,
    CROWDTANGLE_REACTION_TYPES,
    CROWDTANGLE_DEFAULT_TIMEOUT
)

URL_TEMPLATE = (
    'https://api.crowdtangle.com/links'
    '?token=%(token)s'
    '&count=%(count)s'
    '&startDate=%(start_date)s'
    '&includeSummary=true'
    '&link=%(link)s'
    '&sortBy=%(sort_by)s'
)


def forge_url(link, token, start_date, sort_by, include_posts=False):
    return URL_TEMPLATE % {
        'token': token,
        'count': 1 if not include_posts else 100,
        'start_date': start_date,
        'link': quote(link, safe=''),
        'sort_by': sort_by
    }


def crowdtangle_summary(token=None):

    if token is None:
        raise CrowdTangleMissingTokenError
