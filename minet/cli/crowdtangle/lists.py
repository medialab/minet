# =============================================================================
# Minet CrowdTangle Posts CLI Action
# =============================================================================
#
# Logic of the `ct posts` action.
#
import csv

from minet.cli.utils import die
from minet.crowdtangle.constants import CROWDTANGLE_LIST_CSV_HEADERS
from minet.crowdtangle.client import CrowdTangleAPIClient
from minet.crowdtangle.exceptions import CrowdTangleInvalidTokenError


def crowdtangle_lists_action(namespace, output_file):

    client = CrowdTangleAPIClient(namespace.token, rate_limit=namespace.rate_limit)
    writer = csv.writer(output_file)
    writer.writerow(CROWDTANGLE_LIST_CSV_HEADERS)

    try:
        lists = client.lists(format='csv_row')

        for l in lists:
            writer.writerow(l)

    except CrowdTangleInvalidTokenError:
        die([
            'Your API token is invalid.',
            'Check that you indicated a valid one using the `--token` argument.'
        ])
