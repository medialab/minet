# =============================================================================
# Minet Facebook CLI Action
# =============================================================================
#
# Logic of the `fb` action.
#


def facebook_action(namespace):

    if namespace.fb_action == 'comments':
        from minet.cli.facebook.comments import facebook_comments_action

        facebook_comments_action(namespace)
