# =============================================================================
# Minet CrowdTangle Lists CLI Action
# =============================================================================
#
# Logic of the `ct lists` action.
#
import casanova

from minet.cli.crowdtangle.utils import with_crowdtangle_utilities
from minet.crowdtangle.constants import CROWDTANGLE_LIST_CSV_HEADERS


@with_crowdtangle_utilities
def action(cli_args, client):
    writer = casanova.writer(cli_args.output, fieldnames=CROWDTANGLE_LIST_CSV_HEADERS)

    lists = client.lists()

    for l in lists:
        writer.writerow(l)
