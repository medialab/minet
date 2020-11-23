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

    elif namespace.fb_action == 'post-stats':
        from minet.cli.facebook.post_stats import facebook_post_stats_action

        facebook_post_stats_action(namespace)

    elif namespace.fb_action == 'url-likes':
        from minet.cli.facebook.url_likes import facebook_url_likes_action

        facebook_url_likes_action(namespace)

    elif namespace.fb_action == 'url-parse':
        from minet.cli.facebook.url_parse import facebook_url_parse_action

        facebook_url_parse_action(namespace)
