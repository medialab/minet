# =============================================================================
# Minet Twitter Friends CLI Action
# =============================================================================
#
# Logic of the `tw friends` action.
#
import casanova
from minet.twitter.utils import TwitterWrapper

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

    for row, user_id in enricher.cells(namespace.column, with_rows=True):
        all_ids = []

        result = wrapper.call('friends.ids', args={'user_id': user_id})

        if result is not None:
            all_ids = result.get('ids', None)
            for friend_id in all_ids:
                enricher.writerow(row, [friend_id])
