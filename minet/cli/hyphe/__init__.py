# =============================================================================
# Minet Hyphe CLI Action
# =============================================================================
#
# Logic of the `hyphe` action.
#


def hyphe_action(cli_args):

    if cli_args.hyphe_action == 'dump':
        from minet.cli.hyphe.dump import hyphe_dump_action

        hyphe_dump_action(cli_args)
