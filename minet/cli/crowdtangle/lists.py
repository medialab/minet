# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
import csv
import sys
import json
import urllib3
import certifi

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
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
    )

    result = http.request('GET', URL_TEMPLATE % namespace.token)

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
