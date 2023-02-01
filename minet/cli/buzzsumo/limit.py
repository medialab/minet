# =============================================================================
# Minet BuzzSumo Limit CLI Action
# =============================================================================
#
# Logic of the `bz limit` action.
#

# TODO: port this command then attach global fatal errors

from termcolor import colored
from ebbe import format_int

from minet.cli.utils import die
from minet.buzzsumo import BuzzSumoAPIClient
from minet.buzzsumo.exceptions import BuzzSumoInvalidTokenError


def action(cli_args):
    client = BuzzSumoAPIClient(cli_args.token)

    try:
        limit = client.limit()
    except BuzzSumoInvalidTokenError:
        die("Your BuzzSumo token is invalid!")

    print(
        "With your token, you can still make",
        colored(format_int(limit), "green"),
        "calls to the BuzzSumo API until the end of the month.",
    )
