# =============================================================================
# Minet Instagram CLI Action
# =============================================================================
#
# Logic of the `insta` action.
#


def instagram_action(cli_args):

    if cli_args.insta_action == "hashtag":

        from minet.cli.instagram.hashtag import hashtag_action

        hashtag_action(cli_args)
