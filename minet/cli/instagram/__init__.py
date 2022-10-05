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

    if cli_args.insta_action == "user-posts":

        from minet.cli.instagram.user_posts import user_posts_action

        user_posts_action(cli_args)
