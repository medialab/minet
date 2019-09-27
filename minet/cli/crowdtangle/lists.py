# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
import csv
import sys
import json

from minet.utils import create_safe_pool, request
from minet.cli.utils import print_err

URL_TEMPLATE = 'https://api.crowdtangle.com/lists?token=%s'

CSV_HEADERS = [
    'id',
    'title',
    'type'
]


def format_list_for_csv(l):
    return [
        l['id'],
        l['title'],
        l['type']
    ]


def crowdtangle_lists_action(namespace, output_file):
    http = create_safe_pool()

    _, result = request(http, URL_TEMPLATE % namespace.token)

    if result.status == 401:
        print_err('Your API token is invalid.')
        print_err('Check that you indicated a valid one using the `--token` argument.')
        sys.exit(1)

    if result.status >= 400:
        print_err(result.data, result.status)
        sys.exit(1)

    writer = csv.writer(output_file)
    writer.writerow(CSV_HEADERS)

    data = json.loads(result.data)

    for l in data['result']['lists']:
        writer.writerow(format_list_for_csv(l))
