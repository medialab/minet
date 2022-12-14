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

    if cli_args.insta_action == "user-followers":

        from minet.cli.instagram.user_followers import user_followers_action

        user_followers_action(cli_args)

    if cli_args.insta_action == "user-following":

        from minet.cli.instagram.user_following import user_following_action

        user_following_action(cli_args)

    if cli_args.insta_action == "user-infos":

        from minet.cli.instagram.user_infos import user_infos_action

        user_infos_action(cli_args)
