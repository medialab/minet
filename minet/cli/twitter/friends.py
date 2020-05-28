# =============================================================================
# Minet Twitter Friends CLI Action
# =============================================================================
#
# Logic of the `tw friends` action.
#
import casanova
from minet.twitter.utils import TwitterWrapper
from tqdm import tqdm

REPORT_HEADERS = [
    'friends_id'
]


def twitter_friends_action(namespace, output_file):

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

    for row, user_id in enricher.cells(namespace.column, with_rows=True):
        all_ids = []
        next_cursor = 0
        result = None

        wrapper_args = {'user_id': user_id}
        result = wrapper.call('friends.ids', wrapper_args)

        if result is not None:
            all_ids = result.get('ids', [])
            next_cursor = result.get('next_cursor', None)

            for friend_id in all_ids:
                enricher.writerow(row, [friend_id])

            while next_cursor > 0:
                wrapper_args['cursor'] = next_cursor
                result = wrapper.call('friends.ids', wrapper_args)

                if result is not None:
                    all_ids = result.get('ids', [])
                    next_cursor = result.get('next_cursor', None)

                    for friend_id in all_ids:
                        enricher.writerow(row, [friend_id])


        loading_bar.update()

    loading_bar.close()
