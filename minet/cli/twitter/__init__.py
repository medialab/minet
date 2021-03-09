# =============================================================================
# Minet Twitter CLI Action
# =============================================================================
#
# Logic of the `tw` action.
#
import sys

from minet.cli.utils import open_output_file, die


def check_credentials(namespace):

    # Credentials are required to be able to access the API
    if not namespace.api_key or \
       not namespace.api_secret_key or \
       not namespace.access_token or \
       not namespace.access_token_secret:
        die([
            'Full credentials are required to access Twitter API.',
            'You can provide them using various CLI arguments:',
            '    --api-key',
            '    --api-secret-key',
            '    --access-token',
            '    --access-token-secret'
        ])


def twitter_action(namespace):

    output_file = open_output_file(
        namespace.output,
        flag='a+' if getattr(namespace, 'resume', False) else 'w'
    )

    if getattr(namespace, 'resume', False) and not namespace.output:
        die(
            'Cannot --resume if -o/--output is not set!'
        )

    if namespace.tw_action == 'scrape':
        from minet.cli.twitter.scrape import twitter_scrape_action

        twitter_scrape_action(namespace, output_file)

    else:
        check_credentials(namespace)

        if namespace.tw_action == 'friends':
            from minet.cli.twitter.friends import twitter_friends_action

            twitter_friends_action(namespace, output_file)

        elif namespace.tw_action == 'followers':
            from minet.cli.twitter.followers import twitter_followers_action

            twitter_followers_action(namespace, output_file)

        elif namespace.tw_action == 'users':
            from minet.cli.twitter.users import twitter_users_action

            twitter_users_action(namespace, output_file)

        elif namespace.tw_action == 'user-tweets':
            from minet.cli.twitter.user_tweets import twitter_user_tweets_action

            twitter_user_tweets_action(namespace, output_file)

        else:
            raise TypeError('unkown tw_action "%s"' % namespace.tw_action)

    # Cleanup
    if namespace.output is not None:
        output_file.close()
