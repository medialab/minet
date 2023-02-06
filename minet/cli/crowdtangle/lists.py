# =============================================================================
# Minet CrowdTangle Lists CLI Action
# =============================================================================
#
# Logic of the `ct lists` action.
#
import csv

from minet.cli.crowdtangle.utils import with_crowdtangle_fatal_errors
from minet.crowdtangle.constants import CROWDTANGLE_LIST_CSV_HEADERS
from minet.crowdtangle.client import CrowdTangleAPIClient


@with_crowdtangle_fatal_errors
def action(cli_args):

    client = CrowdTangleAPIClient(cli_args.token, rate_limit=cli_args.rate_limit)
    writer = csv.writer(cli_args.output)
    writer.writerow(CROWDTANGLE_LIST_CSV_HEADERS)

    lists = client.lists()

    for l in lists:
        writer.writerow(l)
