# =============================================================================
# Minet BuzzSumo CLI Action
# =============================================================================
#
# Logic of the `bz` action.
#
from argparse import ArgumentTypeError
from datetime import datetime

from minet.cli.argparse import command, subcommand, ConfigAction

FIVE_YEARS_IN_SEC = 5 * 365.25 * 24 * 60 * 60


class BuzzSumoDateType(object):
    def __call__(self, date):
        try:
            timestamp = int(datetime.strptime(date, "%Y-%m-%d").timestamp())
        except ValueError:
            raise ArgumentTypeError(
                "dates should have the following format : YYYY-MM-DD."
            )

        if (datetime.now().timestamp() - timestamp) > FIVE_YEARS_IN_SEC:
            raise ArgumentTypeError(
                "you cannot query BuzzSumo using dates before 5 years ago."
            )

        return timestamp


BUZZSUMO_LIMIT_SUBCOMMAND = subcommand(
    "limit",
    "minet.cli.buzzsumo.limit",
    title="Minet Buzzsumo Limit Command",
    description="""
        Call BuzzSumo for a given request and return the remaining number
        of calls for this month contained in the request's headers.
    """,
    epilog="""
        examples:

        . Returning the remaining number of calls for this month:
            $ minet bz limit --token YOUR_TOKEN
    """,
)


BUZZSUMO_COMMAND = command(
    "buzzsumo",
    "minet.cli.buzzsumo",
    title="Minet Buzzsumo Command",
    description="""
        Gather data from the BuzzSumo APIs easily and efficiently.
    """,
    aliases=["bz"],
    common_arguments=[
        {
            "flags": ["-t", "--token"],
            "help": "BuzzSumo API token.",
            "action": ConfigAction,
            "rc_key": ["buzzsumo", "token"],
        }
    ],
    subcommands=[BUZZSUMO_LIMIT_SUBCOMMAND],
)
