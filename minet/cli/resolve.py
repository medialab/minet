# =============================================================================
# Minet Resolve CLI Action
# =============================================================================
#
from minet.cli.fetch import fetch_action


def resolve_action(cli_args):
    return fetch_action(cli_args, resolve=True)
