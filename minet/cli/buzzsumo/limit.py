# =============================================================================
# Minet BuzzSumo Limit CLI Action
# =============================================================================
#
# Logic of the `bz limit` action.
#
from ebbe import format_int

from minet.buzzsumo import BuzzSumoAPIClient
from minet.cli.utils import colored
from minet.cli.buzzsumo.utils import with_buzzsumo_fatal_errors


@with_buzzsumo_fatal_errors
def action(cli_args):
    client = BuzzSumoAPIClient(cli_args.token)

    limit = client.limit()

    print(
        "With your token, you can still make",
        colored(format_int(limit), "green"),
        "calls to the BuzzSumo API until the end of the month.",
    )
