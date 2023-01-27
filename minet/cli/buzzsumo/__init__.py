# =============================================================================
# Minet BuzzSumo CLI Action
# =============================================================================
#
# Logic of the `bz` action.
#
from minet.cli.argparse import ConfigAction
from minet.cli.commands import command

BUZZSUMO_COMMAND = command(
    "buzzsumo",
    "minet.cli.buzzsumo",
    title="Minet Buzzsumo Command",
    description="""
        Gather data from the BuzzSumo APIs easily and efficiently.
    """,
    common_arguments=[
        {
            "flags": ["-t", "--token"],
            "help": "BuzzSumo API token.",
            "action": ConfigAction,
            "rc_key": ["buzzsumo", "token"],
            "required": True,
        }
    ],
    subcommands=[],
)
