# =============================================================================
# Minet Twitter CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the twitter actions.
#
import casanova
from tqdm import tqdm

from minet.twitter.utils import TwitterWrapper


def make_twitter_action(method_name, csv_headers):

    def action(namespace, output_file):

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
            add=csv_headers
        )

        loading_bar = tqdm(
            desc='Retrieving ids',
            dynamic_ncols=True,
            total=namespace.total,
            unit=' line'
        )

        for row, user in enricher.cells(namespace.column, with_rows=True):
            all_ids = []
            next_cursor = -1
            result = None

            if namespace.id:
                wrapper_args = {'user_id': user}
            else:
                wrapper_args = {'screen_name': user}

            while next_cursor != 0:
                wrapper_args['cursor'] = next_cursor
                method = '%(method_name)s.ids' % {'method_name': method_name}
                result = wrapper.call(method, wrapper_args)

                if result is not None:
                    all_ids = result.get('ids', [])
                    next_cursor = result.get('next_cursor', 0)

                    for friend_id in all_ids:
                        enricher.writerow(row, [friend_id])
                else:
                    next_cursor = 0

            loading_bar.update()

        loading_bar.close()

    return action
