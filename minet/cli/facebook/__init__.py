# =============================================================================
# Minet Facebook CLI Action
# =============================================================================
#
# Logic of the `fb` action.
#


def facebook_action(cli_args):

    if cli_args.fb_action == 'comments':
        from minet.cli.facebook.comments import facebook_comments_action

        facebook_comments_action(cli_args)

    if cli_args.fb_action == 'posts':
        from minet.cli.facebook.posts import facebook_posts_action

        facebook_posts_action(cli_args)

    elif cli_args.fb_action == 'post-authors':
        from minet.cli.facebook.post_authors import facebook_post_authors_action

        facebook_post_authors_action(cli_args)

    elif cli_args.fb_action == 'post-stats':
        from minet.cli.facebook.post_stats import facebook_post_stats_action

        facebook_post_stats_action(cli_args)

    elif cli_args.fb_action == 'url-likes':
        from minet.cli.facebook.url_likes import facebook_url_likes_action

        facebook_url_likes_action(cli_args)
