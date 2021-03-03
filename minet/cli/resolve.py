# =============================================================================
# Minet Resolve CLI Action
# =============================================================================
#
from minet.cli.fetch import fetch_action


def resolve_action(namespace):
    return fetch_action(namespace, resolve=True)
