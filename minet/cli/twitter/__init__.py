# =============================================================================
# Minet Twitter CLI Action
# =============================================================================
#
# Logic of the `tw` action.
#
from minet.cli.utils import die


def check_credentials(cli_args):

    # Credentials are required to be able to access the API
    if not cli_args.api_key or \
       not cli_args.api_secret_key or \
       not cli_args.access_token or \
       not cli_args.access_token_secret:
        die([
            'Full credentials are required to access Twitter API.',
            'You can provide them using various CLI arguments:',
            '    --api-key',
            '    --api-secret-key',
            '    --access-token',
            '    --access-token-secret'
        ])


def twitter_action(cli_args):
    if cli_args.tw_action == 'scrape':
        from minet.cli.twitter.scrape import twitter_scrape_action

        twitter_scrape_action(cli_args)

    else:
        check_credentials(cli_args)

        if cli_args.tw_action == 'friends':
            from minet.cli.twitter.friends import twitter_friends_action

            twitter_friends_action(cli_args)

        elif cli_args.tw_action == 'followers':
            from minet.cli.twitter.followers import twitter_followers_action

            twitter_followers_action(cli_args)

        elif cli_args.tw_action == 'users':
            from minet.cli.twitter.users import twitter_users_action

            twitter_users_action(cli_args)

        elif cli_args.tw_action == 'user-tweets':
            from minet.cli.twitter.user_tweets import twitter_user_tweets_action

            twitter_user_tweets_action(cli_args)

        elif cli_args.tw_action == 'tweet-search':
            from minet.cli.twitter.tweet_search import twitter_tweet_search_action

            twitter_tweet_search_action(cli_args)

        elif cli_args.tw_action == 'tweet-count':
            from minet.cli.twitter.tweet_count import twitter_tweet_count_action

            twitter_tweet_count_action(cli_args)

        elif cli_args.tw_action == 'tweets':
            from minet.cli.twitter.tweets import twitter_tweets_action

            twitter_tweets_action(cli_args)

        elif cli_args.tw_action == 'attrition':
            from minet.cli.twitter.attrition import twitter_attrition_action

            twitter_attrition_action(cli_args)

        elif cli_args.tw_action == 'user-search':
            from minet.cli.twitter.user_search import twitter_user_search_action

            twitter_user_search_action(cli_args)

        elif cli_args.tw_action == 'retweeters':
            from minet.cli.twitter.retweeters import twitter_retweeters_action

            twitter_retweeters_action(cli_args)

        else:
            raise TypeError('unkown tw_action "%s"' % cli_args.tw_action)
