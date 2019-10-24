# =============================================================================
# Minet Hyphe CLI Action
# =============================================================================
#
# Logic of the `hyphe` action.
#


def hyphe_action(namespace):

    if namespace.hyphe_action == 'dump':
        from minet.cli.hyphe.dump import hyphe_dump_action

        hyphe_dump_action(namespace)
