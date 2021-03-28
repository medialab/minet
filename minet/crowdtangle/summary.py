# =============================================================================
# Minet CrowdTangle Links Summary
# =============================================================================
#
# Function related to link summary using CrowdTangle's APIs.
#
from urllib.parse import quote

from minet.crowdtangle.exceptions import (
    CrowdTangleMissingTokenError,
    CrowdTangleInvalidTokenError,
    CrowdTangleInvalidRequestError
)
from minet.utils import nested_get
from minet.web import request_json
from minet.crowdtangle.constants import (
    CROWDTANGLE_SUMMARY_DEFAULT_SORT_TYPE,
    CROWDTANGLE_SUMMARY_SORT_TYPES,
    CROWDTANGLE_OUTPUT_FORMATS
)
from minet.crowdtangle.formatters import (
    format_post,
    format_summary
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


def url_forge(link, token, start_date, sort_by, platforms=None, include_posts=False):

    base_url = URL_TEMPLATE % {
        'token': token,
        'count': 1 if not include_posts else 1000,
        'start_date': start_date,
        'link': quote(link, safe=''),
        'sort_by': sort_by
    }

    if platforms:
        base_url += '&platforms=%s' % ','.join(platforms)

    return base_url


def crowdtangle_summary(pool, link, token=None, start_date=None, with_top_posts=False,
                        sort_by=CROWDTANGLE_SUMMARY_DEFAULT_SORT_TYPE, format='csv_dict_row', platforms=None):

    if token is None:
        raise CrowdTangleMissingTokenError

    if format not in CROWDTANGLE_OUTPUT_FORMATS:
        raise TypeError('minet.crowdtangle.summary: unkown `format`.')

    if not isinstance(start_date, str):
        raise TypeError('minet.crowdtangle.summary: expecting a `start_date` kwarg.')

    if sort_by not in CROWDTANGLE_SUMMARY_SORT_TYPES:
        raise TypeError('minet.crowdtangle.summary: unknown `sort_by`.')

    # Fetching
    api_url = url_forge(
        link,
        token,
        start_date,
        sort_by,
        platforms,
        with_top_posts
    )

    err, response, data = request_json(api_url, pool=pool)

    if err is not None:
        raise err

    if response.status == 401:
        raise CrowdTangleInvalidTokenError

    if response.status >= 400:
        raise CrowdTangleInvalidRequestError(api_url)

    stats = nested_get(['result', 'summary', 'facebook'], data)
    posts = nested_get(['result', 'posts'], data) if with_top_posts else None

    if stats is not None:
        if format == 'csv_dict_row':
            stats = format_summary(stats, as_dict=True)
        elif format == 'csv_row':
            stats = format_summary(stats)

    if not with_top_posts:
        return stats

    else:
        if posts is not None:
            if format == 'csv_dict_row':
                posts = [format_post(post, as_dict=True) for post in posts]
            elif format == 'csv_row':
                posts = [format_post(post) for post in posts]

        return stats, posts
