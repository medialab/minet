# =============================================================================
# Minet CrowdTangle Links Summary CLI Action
# =============================================================================
#
# Logic of the `ct summary` action.
#
import csv
from io import StringIO
from urllib.parse import quote
from tqdm import tqdm
from ural import is_url

from minet.utils import create_pool, request_json, RateLimiter, nested_get
from minet.cli.utils import die, custom_reader

from minet.cli.crowdtangle.constants import (
    CROWDTANTLE_LINKS_DEFAULT_RATE_LIMIT,
    CROWDTANGLE_REACTION_TYPES,
    CROWDTANGLE_DEFAULT_TIMEOUT
)

URL_TEMPLATE = (
    'https://api.crowdtangle.com/links'
    '?token=%(token)s'
    '&count=1'
    '&startDate=%(start_date)s'
    '&includeSummary=true'
    '&link=%(link)s'
)


def forge_url(namespace, link):
    return URL_TEMPLATE % {
        'token': namespace.token,
        'start_date': namespace.start_date,
        'link': quote(link, safe='')
    }


CSV_HEADERS = ['%s_count' % t for t in CROWDTANGLE_REACTION_TYPES]
CSV_PADDING = ['0'] * len(CSV_HEADERS)


def format_summary_for_csv(stats):
    return [stats['%sCount' % t] for t in CROWDTANGLE_REACTION_TYPES]


def crowdtangle_summary_action(namespace, output_file):
    if not namespace.start_date:
        die('Missing --start-date!')

    http = create_pool(timeout=CROWDTANGLE_DEFAULT_TIMEOUT)

    if is_url(namespace.column):
        namespace.file = StringIO('url\n%s' % namespace.column)
        namespace.column = 'url'

    input_headers, pos, reader = custom_reader(namespace.file, namespace.column)

    output_headers = input_headers + CSV_HEADERS
    output_writer = csv.writer(output_file)
    output_writer.writerow(output_headers)

    rate_limit = namespace.rate_limit if namespace.rate_limit is not None else CROWDTANTLE_LINKS_DEFAULT_RATE_LIMIT
    rate_limiter = RateLimiter(rate_limit, 60.0)

    loading_bar = tqdm(
        desc='Collecting data',
        dynamic_ncols=True,
        total=namespace.total,
        unit=' urls'
    )

    for line in reader:
        with rate_limiter:
            link = line[pos]

            # Fetching
            err, response, data = request_json(http, forge_url(namespace, link))

            # Handling errors
            if err:
                die(err)
            elif response.status == 401:
                die([
                    'Your API token is invalid.',
                    'Check that you indicated a valid one using the `--token` argument.'
                ])
            elif response.status >= 400:
                die(response.data, response.status)

            summary = nested_get(['result', 'summary', 'facebook'], data)

            if summary is None:
                output_writer.writerow(line + CSV_PADDING)
            else:
                output_writer.writerow(line + format_summary_for_csv(summary))

            loading_bar.update()
