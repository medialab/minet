# =============================================================================
# Minet BuzzSumo CLI Action
# =============================================================================
#
# Logic of the `bz` action.
#
import sys

from minet.cli.utils import die


def buzzsumo_action(cli_args):

    # A token is needed to be able to access the API
    if not cli_args.token:
        die([
            'A token is needed to be able to access BuzzSumo\'s API.',
            'You can provide one using the `--token` argument.'
        ])

    if cli_args.bz_action == 'limit':
        from minet.cli.buzzsumo.limit import buzzsumo_limit_action

        buzzsumo_limit_action(cli_args)
