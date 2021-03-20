# =============================================================================
# Minet Google CLI Action
# =============================================================================
#
# Logic of the `google` action.
#
from minet.cli.utils import die, open_output_file


def google_action(namespace):

    if namespace.google_action == 'sheets':
        from minet.cli.google.sheets import google_sheets_action
        google_sheets_action(namespace)
