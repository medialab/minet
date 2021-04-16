# =============================================================================
# Minet Google CLI Action
# =============================================================================
#
# Logic of the `google` action.
#
from minet.cli.utils import die


def google_action(cli_args):

    if cli_args.google_action == 'sheets':
        from minet.cli.google.sheets import google_sheets_action
        google_sheets_action(cli_args)
