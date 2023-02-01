# =============================================================================
# Minet BuzzSumo Limit CLI Action
# =============================================================================
#
# Logic of the `bz limit` action.
#

# TODO: port this command then attach global fatal errors
# TODO: check pyinstaller and be wary of lazyloading utils, or divide sub .commands,
# TODO: debug lazyloading by tracking imports

from termcolor import colored
from ebbe import format_int

from minet.cli.utils import die, register_retryer_logger
from minet.buzzsumo import BuzzSumoAPIClient
from minet.buzzsumo.exceptions import BuzzSumoInvalidTokenError


def buzzsumo_limit_action(cli_args):
    register_retryer_logger()

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
