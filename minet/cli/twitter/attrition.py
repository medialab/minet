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
        add=['attrition_reason'],
        total=cli_args.total
    )

    loading_bar = LoadingBar(
        'Retrieving attrition reason',
        total=enricher.total,
        unit='user'
    )

    indexed_results = {}

    indexed_tweets = {}

    result = None

    if cli_args.column_tweets not in enricher.headers:
        raise InvalidArgumentsError('Could not find the "%s" column containing the tweet ids in the given CSV file.' % cli_args.column_tweets)
    if cli_args.column_users not in enricher.headers:
        raise InvalidArgumentsError('Could not find the "%s" column containing the user ids in the given CSV file.' % cli_args.column_users)

    user_id_column = cli_args.column_users

    user_id_pos = enricher.headers[user_id_column]

    for chunk in as_chunks(100, enricher.cells(cli_args.column_tweets, with_rows=True)):
        tweets = ','.join(row[1] for row in chunk)
        kwargs = {'_id': tweets}

        try:
            result = client.call(['statuses', 'lookup'], **kwargs)

        except TwitterHTTPError as e:
            loading_bar.inc('errors')
            raise e

        for tw in result:
            indexed_tweets[tw['id_str']] = 1

        for row, tweet in chunk:
            user = row[user_id_pos]

            if tweet in indexed_tweets:
                indexed_results[tweet] = 'tweet_ok'

            else:
                if tweet not in indexed_results:
                    client_args = {'user_id': user}

                    try:
                        result = client.call(['users', 'show'], **client_args)

                    except TwitterHTTPError as e:
                        if e.e.code == 403 and getpath(e.response_data, ['errors', 0, 'code'], '') == 63:
                            indexed_results[tweet] = 'suspended_user'

                        elif e.e.code == 404 and getpath(e.response_data, ['errors', 0, 'code'], '') == 50:
                            indexed_results[tweet] = 'deleted_user'

                        else:
                            raise e

                    if result is not None:
                        if result['protected']:
                            indexed_results[tweet] = 'protected_user'
                        else:
                            indexed_results[tweet] = 'tweet_deleted'

            enricher.writerow(row, [indexed_results[tweet]])
            result = None
            loading_bar.update()
