# =============================================================================
# Minet Twitter CLI Action
# =============================================================================
#
# Logic of the `tw` action.
#
import sys

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

        else:
            raise TypeError('unkown tw_action "%s"' % cli_args.tw_action)
