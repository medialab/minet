# =============================================================================
# Minet Twitter Users CLI Action
# =============================================================================
#
# Logic of the `tw users` action.

import casanova
from minet.twitter.utils import TwitterWrapper, clean_user_entities, get_timestamp
from tqdm import tqdm
from datetime import datetime

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

def get_data(result, user):

    data_indexed = {}

    for element in result:
        clean_user_entities(element)

        if user == 'id':
            user_index = element.get('id_str')
        else:
            user_index = element.get('screen_name')

        getter = lambda element, key: element.get(key) if key != "created_at_iso" else datetime.strptime(element.get("created_at"), '%a %b %d %H:%M:%S +0000 %Y').isoformat()
        data = [getter(element, key) for key in REPORT_HEADERS]

        data_indexed[user_index] = data

    return data_indexed


def gen_chunks(column, enricher, length):
    chunk = []

    for row, user in enricher.cells(column, with_rows=True):

        if len(chunk) == length:
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

    for chunk in gen_chunks(column, enricher, 100):

        result = None
        clean_result = []

        all_users = [row[0] for row in chunk if row[0]]
        list_user = ",".join(all_users)

        if namespace.id:
            wrapper_args = {'user_id': list_user}
            user = 'id'
        else:
            wrapper_args = {'screen_name': list_user}
            user = 'screen_name'

        result = wrapper.call('users.lookup', wrapper_args)

        if result is not None:
            data = get_data(result, user)

            for item in chunk:
                user, line = item

                if user in data.keys():
                    enricher.writerow(line, data[user])
                else:
                    enricher.writerow(line)

        loading_bar.update(len(chunk))

    loading_bar.close()
