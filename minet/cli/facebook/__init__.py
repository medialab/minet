# =============================================================================
# Minet Facebook CLI Action
# =============================================================================
#
# Logic of the `fb` action.
#
import sys

from minet.cli.utils import DummyTqdmFile, print_err


def facebook_action(namespace):

    if namespace.fb_action == 'comments':
        from minet.cli.facebook.comments import facebook_comments_action

        facebook_comments_action(namespace)
