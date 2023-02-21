# =============================================================================
# Minet BuzzSumo Limit CLI Action
# =============================================================================
#
# Logic of the `bz limit` action.
#
from ebbe import format_int

from minet.buzzsumo import BuzzSumoAPIClient
from minet.cli.console import console
from minet.cli.buzzsumo.utils import with_buzzsumo_fatal_errors


@with_buzzsumo_fatal_errors
def action(cli_args):
    client = BuzzSumoAPIClient(cli_args.token)

    limit = client.limit()

    console.log_with_time(
        "With your token, you can still make",
        "[info]%s[/info]" % format_int(limit),
        "calls to the BuzzSumo API until the end of the month.",
    )
