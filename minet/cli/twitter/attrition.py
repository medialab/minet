# =============================================================================
# Minet Twitter Attrition CLI Action
# =============================================================================
#
# Logic of the `tw attrition` action.
#
import casanova
from twitter import TwitterHTTPError
from ebbe import getpath, as_chunks

from minet.cli.utils import LoadingBar
from minet.cli.exceptions import InvalidArgumentsError
from minet.twitter import TwitterAPIClient


def twitter_attrition_action(cli_args):

    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key
    )

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=['tweet_current_status'],
        total=cli_args.total
    )

    loading_bar = LoadingBar(
        'Retrieving attrition reason',
        total=enricher.total,
        unit='user'
    )

    indexed_tweets = set()

    # NOTE: currently this index is unbounded and could potentially
    # exhaust the user's memory even if unlikely (the index is bounded
    # by the total number of users of unvailable tweets in input dataset)
    indexed_users = {}

    result = None

    if cli_args.tweet_column not in enricher.headers:
        raise InvalidArgumentsError('Could not find the "%s" column containing the tweet ids in the given CSV file.' % cli_args.tweet_column)

    if cli_args.user_column not in enricher.headers:
        raise InvalidArgumentsError('Could not find the "%s" column containing the user ids in the given CSV file.' % cli_args.user_column)

    user_id_column = cli_args.user_column
    user_id_pos = enricher.headers[user_id_column]

    for chunk in as_chunks(100, enricher.cells(cli_args.tweet_column, with_rows=True)):
        tweets = ','.join(row[1] for row in chunk)
        kwargs = {'_id': tweets}

        try:
            result = client.call(['statuses', 'lookup'], **kwargs)

        except TwitterHTTPError as e:
            loading_bar.inc('errors')
            raise e

        for tw in result:
            indexed_tweets.add(tw['id_str'])

        for row, tweet in chunk:
            loading_bar.update()

            user = row[user_id_pos]

            if tweet in indexed_tweets:
                current_tweet_status = 'available_tweet'
                enricher.writerow(row, [current_tweet_status])
                continue

            if user not in indexed_users:
                if cli_args.ids:
                    client_args = {'user_id': user}
                else:
                    client_args = {'screen_name': user}

                result_user = None

                try:
                    result_user = client.call(['users', 'show'], **client_args)

                except TwitterHTTPError as e:
                    loading_bar.print(e.response_data)
                    if e.e.code == 403 and getpath(e.response_data, ['errors', 0, 'code'], '') == 63:
                        indexed_users[user] = 'suspended_user'

                    elif e.e.code == 404 and getpath(e.response_data, ['errors', 0, 'code'], '') == 50:
                        indexed_users[user] = 'deactivated_user'

                    else:
                        raise e

                if result_user is not None:
                    if result_user['protected']:
                        indexed_users[user] = 'protected_user'
                    else:
                        indexed_users[user] = 'user_ok'

            if indexed_users[user] == 'user_ok':
                current_tweet_status = 'original_tweet_ok'

                if cli_args.retweeted_id:
                    original_id_pos = enricher.headers[cli_args.retweeted_id]
                    original_tweet = row[original_id_pos]
                    client_arg = {'_id': original_tweet}
                    result_retweet = None
                    current_tweet_status = 'original_tweet_ok'

                    if original_tweet:
                        try:
                            result_retweet = client.call(['statuses', 'show'], **client_arg)

                        except TwitterHTTPError as e:
                            if e.e.code == 403 and getpath(e.response_data, ['errors', 0, 'code'], '') == 63:
                                current_tweet_status = 'original_user_suspended'

                            elif e.e.code == 403 and getpath(e.response_data, ['errors', 0, 'code'], '') == 179:
                                current_tweet_status = 'original_user_protected'

                            elif e.e.code == 404 and (getpath(e.response_data, ['errors', 0, 'code'], '') == 144 or getpath(e.response_data, ['errors', 0, 'code'], '') == 34):
                                current_tweet_status = 'original_tweet_unavailable'

                            else:
                                raise e

                        if result_retweet is not None:
                            current_tweet_status = 'unavailable_retweet'

                if current_tweet_status == 'original_tweet_ok':
                    current_tweet_status = 'unavailable_tweet'

            else:
                current_tweet_status = indexed_users[user]

            enricher.writerow(row, [current_tweet_status])
