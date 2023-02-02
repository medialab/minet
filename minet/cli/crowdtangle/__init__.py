# =============================================================================
# Minet CrowdTangle CLI Action
# =============================================================================
#
# Logic of the `ct` action.
#
from minet.cli.argparse import command, subcommand, ConfigAction
from minet.cli.exceptions import InvalidArgumentsError

# TODO: lazy loading constants
CROWDTANGLE_DEFAULT_RATE_LIMIT = 6

# TODO: this should probably be a required instead, see #534
def check_token(cli_args):
    if not cli_args.token:
        raise InvalidArgumentsError(
            [
                "A token is needed to be able to access CrowdTangle's API.",
                "You can provide one using the `--token` argument.",
            ]
        )


def crowdtangle_api_subcommand(*args, **kwargs):
    return subcommand(*args, validate=check_token, **kwargs)


CROWDTANGLE_COMMAND = command(
    "crowdtangle",
    "minet.cli.crowdtangle",
    "Minet Crowdtangle Command",
    aliases=["ct"],
    description="""
        Gather data from the CrowdTangle APIs easily and efficiently.
    """,
    common_arguments=[
        {
            "flag": "--rate-limit",
            "help": "Authorized number of hits by minutes. Defaults to %i. Rcfile key: crowdtangle.rate_limit"
            % CROWDTANGLE_DEFAULT_RATE_LIMIT,
            "type": int,
            "default": CROWDTANGLE_DEFAULT_RATE_LIMIT,
            "rc_key": ["crowdtangle", "rate_limit"],
            "action": ConfigAction,
        },
        {
            "flags": ["-t", "--token"],
            "help": "CrowdTangle dashboard API token. Rcfile key: crowdtangle.token",
            "action": ConfigAction,
            "rc_key": ["crowdtangle", "token"],
        },
    ],
    subcommands=[],
)
