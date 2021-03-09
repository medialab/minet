# =============================================================================
# Minet Twitter User Tweets CLI Action
# =============================================================================
#
# Logic of the `tw user-tweets` action.
#
import casanova
from twitwi import (
    TwitterWrapper,
    # normalize_tweet,
    # format_tweet_as_csv_row
)
from twitwi.constants import TWEET_FIELDS
# from ebbe import as_chunks

from minet.cli.utils import LoadingBar


def twitter_user_tweets_action(namespace, output_file):

    wrapper = TwitterWrapper(
        namespace.access_token,
        namespace.access_token_secret,
        namespace.api_key,
        namespace.api_secret_key
    )

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=TWEET_FIELDS
    )

    loading_bar = LoadingBar(
        'Retrieving tweets',
        total=namespace.total,
        unit='tweet'
    )

    for row, user in enricher.cells(namespace.column, with_rows=True):
        print(user)

    # for chunk in as_chunks(enricher.cells(100, namespace.column, with_rows=True)):
    #     users = ','.join(row[1] for row in chunk)

    #     if namespace.ids:
    #         wrapper_args = {'user_id': users}
    #         key = 'id'
    #     else:
    #         wrapper_args = {'screen_name': users}
    #         key = 'screen_name'

    #     result = wrapper.call(['users', 'lookup'], **wrapper_args)

    #     if result is not None:
    #         indexed_result = {}

    #         for user in result:
    #             user = normalize_user(user)
    #             user_row = format_user_as_csv_row(user)
    #             indexed_result[user[key]] = user_row

    #         for row, user in chunk:
    #             user_row = indexed_result.get(user)

    #             enricher.writerow(row, user_row)

    #     loading_bar.update(len(chunk))

    # loading_bar.close()
