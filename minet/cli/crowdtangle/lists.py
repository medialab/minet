# =============================================================================
# Minet CrowdTangle Lists CLI Action
# =============================================================================
#
# Logic of the `ct lists` action.
#
import csv

from minet.cli.utils import die
from minet.crowdtangle.constants import CROWDTANGLE_LIST_CSV_HEADERS
from minet.crowdtangle.client import CrowdTangleAPIClient
from minet.crowdtangle.exceptions import CrowdTangleInvalidTokenError


def crowdtangle_lists_action(cli_args):

    client = CrowdTangleAPIClient(cli_args.token, rate_limit=cli_args.rate_limit)
    writer = csv.writer(cli_args.output)
    writer.writerow(CROWDTANGLE_LIST_CSV_HEADERS)

    try:
        lists = client.lists()

        for l in lists:
            writer.writerow(l)

    except CrowdTangleInvalidTokenError:
        die(
            [
                "Your API token is invalid.",
                "Check that you indicated a valid one using the `--token` argument.",
            ]
        )
