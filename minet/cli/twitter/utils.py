# =============================================================================
# Minet Twitter CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the twitter actions.
#
import casanova
import sys
from tqdm import tqdm
from twitwi import TwitterWrapper
from twitter import TwitterHTTPError


def make_twitter_action(method_name, csv_headers):

    def action(namespace, output_file):

        # TODO: this is temp debug
        def listener(event, data):
            tqdm.write(event, file=sys.stderr)
            tqdm.write(repr(data), file=sys.stderr)

        wrapper = TwitterWrapper(
            namespace.access_token,
            namespace.access_token_secret,
            namespace.api_key,
            namespace.api_secret_key,
            listener=listener
        )

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
            unit=' followers',
            postfix={
                'users': 0
            }
        )

        users_done = 0
        users_not_found = 0

        def update_stats():
            kwargs = {
                'users': users_done
            }

            if users_not_found:
                kwargs['not_found'] = users_not_found

            loading_bar.set_postfix(**kwargs)

        for row, user in enricher.cells(namespace.column, with_rows=True):
            all_ids = []
            next_cursor = -1
            result = None

            if namespace.ids:
                wrapper_kwargs = {'user_id': user}
            else:
                wrapper_kwargs = {'screen_name': user}

            while next_cursor != 0:
                wrapper_kwargs['cursor'] = next_cursor

                try:
                    result = wrapper.call([method_name, 'ids'], **wrapper_kwargs)
                except TwitterHTTPError as e:

                    # The user does not exist
                    users_not_found += 1
                    update_stats()
                    break

                if result is not None:
                    all_ids = result.get('ids', [])
                    next_cursor = result.get('next_cursor', 0)

                    loading_bar.update(len(all_ids))

                    for user_id in all_ids:
                        enricher.writerow(row, [user_id])
                else:
                    next_cursor = 0

            users_done += 1
            update_stats()

        loading_bar.close()

    return action
