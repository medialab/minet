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

        # First we need to query a batch of tweet ids at once to figure out
        # whether they are still available or not
        try:
            result = client.call(['statuses', 'lookup'], **kwargs)

        except TwitterHTTPError as e:
            loading_bar.inc('errors')
            raise e

        for tw in result:
            indexed_tweets.add(tw['id_str'])

        for row, tweet in chunk:
            loading_bar.update()

            if tweet in indexed_tweets:
                current_tweet_status = 'available_tweet'
                enricher.writerow(row, [current_tweet_status])
                continue

            # If tweet is not available, we will query once more to find out
            # what the reason for its unavailability is

            client_args = {'_id': tweet}

            current_tweet_status = 'unknown'

            result_tweet = None

            try:
                result_tweet = client.call(['statuses', 'show'], **client_args)

            except TwitterHTTPError as e:
                if e.e.code == 403 and getpath(e.response_data, ['errors', 0, 'code'], '') == 63:
                    current_tweet_status = 'suspended_user'

                elif e.e.code == 403 and getpath(e.response_data, ['errors', 0, 'code'], '') == 179:
                    current_tweet_status = 'protected_user'

                elif e.e.code == 404 and (getpath(e.response_data, ['errors', 0, 'code'], '') == 144 or getpath(e.response_data, ['errors', 0, 'code'], '') == 34):
                    current_tweet_status = 'user_or_tweet_deleted'

                else:
                    raise e

            if result_tweet:
                current_tweet_status = 'available_tweet'

            if current_tweet_status == 'user_or_tweet_deleted' or current_tweet_status == 'unknown':
                user = row[user_id_pos]

                if cli_args.ids:
                    c_args = {'user_id': user}
                else:
                    c_args = {'screen_name': user}

                try:
                    result_user = client.call(['users', 'show'], **c_args)

                except TwitterHTTPError as e:
                    if e.e.code == 404 and getpath(e.response_data, ['errors', 0, 'code'], '') == 50:
                        current_tweet_status = 'deactivated_user'

                if result_user:
                    current_tweet_status = 'unavailable_tweet'

                # Sometimes, the unavailable tweet is a retweet, in which
                # case we need to enquire about the original tweet to find
                # a reason for the tweet's unavailability
                if cli_args.retweeted_id:

                    if current_tweet_status == 'unavailable_tweet' or current_tweet_status == 'unknown':

                        if cli_args.has_dummy_csv:
                            original_tweet = cli_args.retweeted_id
                        else:
                            original_id_pos = enricher.headers[cli_args.retweeted_id]
                            original_tweet = row[original_id_pos]

                        client_arg = {'_id': original_tweet}
                        result_retweet = None

                        if original_tweet:
                            try:
                                result_retweet = client.call(['statuses', 'show'], **client_arg)

                            except TwitterHTTPError as e:
                                if e.e.code == 403 and getpath(e.response_data, ['errors', 0, 'code'], '') == 63:
                                    current_tweet_status = 'suspended_retweeted_user'

                                elif e.e.code == 403 and getpath(e.response_data, ['errors', 0, 'code'], '') == 179:
                                    current_tweet_status = 'protected_retweeted_user'

                                elif e.e.code == 404 and (getpath(e.response_data, ['errors', 0, 'code'], '') == 144 or getpath(e.response_data, ['errors', 0, 'code'], '') == 34):
                                    current_tweet_status = 'unavailable_retweeted_tweet'

                                else:
                                    raise e

                            if result_retweet is not None:
                                current_tweet_status = 'unavailable_retweet'

                if current_tweet_status == 'unknown':
                    current_tweet_status = 'unavailable_tweet'

            enricher.writerow(row, [current_tweet_status])
