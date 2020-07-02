# =============================================================================
# Minet Twitter Users CLI Action
# =============================================================================
#
# Logic of the `tw users` action.

import casanova
from minet.twitter.utils import TwitterWrapper, clean_user_entities, get_timestamp
from minet.utils import chunks_iter
from tqdm import tqdm
import datetime

REPORT_HEADERS = [
    'id_str',
    'screen_name',
    'name',
    'location',
    'created_at_utc',
    'created_at_iso_local',
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


def get_data(result, key):

    data_indexed = {}
    locale = datetime.datetime.now(datetime.timezone(datetime.timedelta(0))).astimezone().tzinfo

    for element in result:
        clean_user_entities(element)

        user_index = element.get(key)

        def getter(element, k):
            if k != 'created_at_iso_local':
                return element.get(k)
            else:
                return get_timestamp(element.get('created_at'), locale)

        data = [getter(element, key) for key in REPORT_HEADERS]

        data_indexed[user_index] = data

    return data_indexed


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

    for chunk in chunks_iter(enricher.cells(namespace.column, with_rows=True), 100):
        users = ','.join(row[1] for row in chunk)

        if namespace.id:
            wrapper_args = {'user_id': users}
            key = 'id_str'
        else:
            wrapper_args = {'screen_name': users}
            key = 'screen_name'

        result = wrapper.call('users.lookup', wrapper_args)

        if result is not None:
            data = get_data(result, key)

            for row, user in chunk:
                if user in data.keys():
                    enricher.writerow(row, data[user])
                else:
                    enricher.writerow(row)

        loading_bar.update(len(chunk))

    loading_bar.close()
