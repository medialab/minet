# =============================================================================
# Minet Twitter Users CLI Action
# =============================================================================
#
# Logic of the `tw users` action.

import casanova
from minet.twitter.utils import TwitterWrapper
from tqdm import tqdm

REPORT_HEADERS = [
    'screen_name',
    'name',
    'location',
    'description',
    'url',
    'protected',
    'followers_count',
    'friends_count',
    'favourites_count',
    'listed_count',
    'statuses_count',
    'created_at',
    'verified'
]

def twitter_users_action(namespace, output_file):

    TWITTER = {
        'access_token': namespace.access_token,
        'access_token_secret': namespace.access_token_secret,
        'api_key': namespace.api_key,
        'api_secret_key': namespace.api_secret_key
    }

    wrapper = TwitterWrapper(TWITTER)

    enricher = casanova.enricher(
        namespace.file,
        output_file,
        keep=namespace.select,
        add=REPORT_HEADERS
    )

    loading_bar = tqdm(
        desc='Retrieving ids',
        dynamic_ncols=True,
        total=namespace.total,
        unit=' line'
    )

    for row, user in enricher.cells(namespace.column, with_rows=True):
        result = None

        if namespace.id:
            wrapper_args = {'user_id': user}
        else:
            wrapper_args = {'screen_name': user}

        result = wrapper.call('users.show', wrapper_args)

        if result is not None:
            screen_name = result.get('screen_name', None)
            name = result.get('name', None)
            location = result.get('location', None)
            description = result.get('description', None)
            url = result.get('url', None)
            protected = result.get('protected', None)
            followers_count = result.get('followers_count', None)
            friends_count = result.get('friends_count', None)
            favourites_count = result.get('favourites_count', None)
            listed_count = result.get('listed_count', None)
            statuses_count = result.get('statuses_count', None)
            created_at = result.get('created_at', None)
            verified = result.get('verified', None)

            enricher.writerow(row, [screen_name, name, location, description, url, protected, followers_count, friends_count, favourites_count, listed_count, statuses_count, created_at, verified])

        loading_bar.update()

    loading_bar.close()
