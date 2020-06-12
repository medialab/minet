# =============================================================================
# Minet Twitter Users CLI Action
# =============================================================================
#
# Logic of the `tw users` action.

import casanova
from minet.twitter.utils import TwitterWrapper, clean_user_entities, get_timestamp
from tqdm import tqdm


REPORT_HEADERS = [
    'id_str',
    'screen_name',
    'name',
    'location',
    'created_at',
    'created_at_iso',
    'description',
    'url',
    'protected',
    'verified',
    'followers_count',
    'friends_count',
    'favourites_count',
    'listed_count',
    'statuses_count',
    'default_profile',
    'default_profile_image',
    'profile_image_url_https',
    'profile_banner_url'
]

def get_data(result):

    data_indexed = {}
    locale = None

    for element in result:
        clean_user_entities(element)

        id_str = element.get('id_str', None)
        screen_name = element.get('screen_name', None)
        name = element.get('name', None)
        location = element.get('location', None)
        created_at = element.get('created_at', None)
        created_at_iso = get_timestamp(created_at, locale)
        description = element.get('description', None)
        url =  element.get('url', None)
        protected = element.get('protected', None)
        verified = element.get('verified', None)
        followers_count = element.get('followers_count', None)
        friends_count = element.get('friends_count', None)
        favourites_count = element.get('favourites_count', None)
        listed_count = element.get('listed_count', None)
        statuses_count = element.get('statuses_count', None)
        default_profile = element.get('default_profile', None)
        default_profile_image = element.get('default_profile_image', None)
        profile_image_url_https = element.get('profile_image_url_https', None)
        profile_banner_url = element.get('profile_banner_url', None)

        data  = [
            id_str,
            screen_name,
            name,
            location,
            created_at,
            created_at_iso,
            description,
            url,
            protected,
            verified,
            followers_count,
            friends_count,
            favourites_count,
            listed_count,
            statuses_count,
            default_profile,
            default_profile_image,
            profile_image_url_https,
            profile_banner_url
        ]

        data_indexed[id_str] = data

    return data_indexed

def gen_chunks(column, enricher):
    chunk = []

    for row, user in enricher.cells(column, with_rows=True):

        if len(chunk) == 100:
            yield chunk
            chunk.clear()

        chunk.append((user, row))

    yield chunk


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

    column = namespace.column

    for chunk in gen_chunks(column, enricher):

        result = None
        clean_result = []

        all_users = [row[0] for row in chunk if row[0]]
        list_user = ",".join(all_users)

        if namespace.id:
            wrapper_args = {'user_id': list_user}
        else:
            wrapper_args = {'screen_name': list_user}

        result = wrapper.call('users.lookup', wrapper_args)

        if result is not None:
            data = get_data(result)
            for item in chunk:
                user, line = item
                enricher.writerow(line, data[user])

        loading_bar.update(len(chunk))

    loading_bar.close()
