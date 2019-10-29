# =============================================================================
# Minet CrowdTangle Links Summary CLI Action
# =============================================================================
#
# Logic of the `ct summary` action.
#
import csv
import json
from urllib.parse import quote

from minet.utils import create_pool, request, RateLimiter
from minet.cli.utils import print_err, die

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


CSV_HEADERS = [

]


def format_list_for_csv(item):
    return [

    ]


def crowdtangle_summary_action(namespace, output_file):
    if not namespace.start_date:
        die('Missing --start-date!')

    http = create_pool()

    url = forge_url(namespace, 'http://lemonde.fr')

    print_err('Using the following starting url:')
    print_err(url)
    print_err()

    print(namespace, output_file)

    # _, result = request(http, URL_TEMPLATE % namespace.token)

    # if result.status == 401:
    #     print_err('Your API token is invalid.')
    #     print_err('Check that you indicated a valid one using the `--token` argument.')
    #     sys.exit(1)

    # if result.status >= 400:
    #     print_err(result.data, result.status)
    #     sys.exit(1)

    # writer = csv.writer(output_file)
    # writer.writerow(CSV_HEADERS)

    # data = json.loads(result.data)

    # for l in data['result']['lists']:
    #     writer.writerow(format_list_for_csv(l))
