# =============================================================================
# Minet Twitter CLI Utils
# =============================================================================
#
# Miscellaneous generic functions used throughout the twitter actions.
#
import casanova
import sys
from ebbe import with_is_last
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
            add=csv_headers + ['cursor'],
            resumable=namespace.resume,
            auto_resume=False
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
        skipped = 0

        def update_stats():
            kwargs = {
                'users': users_done
            }

            if users_not_found:
                kwargs['not_found'] = users_not_found

            if skipped:
                kwargs['skipped'] = skipped

            loading_bar.set_postfix(**kwargs)

        last_batch = None

        if namespace.resume:
            # TODO: sacralize this in specialized casanova enricher
            last_batch = casanova.reverse_reader.last_batch(
                output_file.name,
                batch_value=namespace.column,
                batch_cursor='cursor',
                end_symbol='end'
            )

        for row, user in enricher.cells(namespace.column, with_rows=True):
            if last_batch:
                if user != last_batch.value:
                    skipped += 1
                    update_stats()
                    continue

                if user == last_batch.value and last_batch.finished:
                    last_batch = None
                    skipped += 1
                    update_stats()
                    continue

            all_ids = []
            next_cursor = -1
            result = None

            if last_batch and last_batch.cursor:
                next_cursor = last_batch.cursor

            if namespace.ids:
                wrapper_kwargs = {'user_id': user}
            else:
                wrapper_kwargs = {'screen_name': user}

            while next_cursor != 0:
                wrapper_kwargs['cursor'] = next_cursor

                skip_in_output = None

                if last_batch:
                    skip_in_output = set(row[-2] for row in last_batch.rows)
                    last_batch = None

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

                    for is_last, user_id in with_is_last(all_ids):
                        if skip_in_output and user_id in skip_in_output:
                            continue

                        if is_last:
                            addendum = [user_id, next_cursor or 'end']
                        else:
                            addendum = [user_id, '']

                        enricher.writerow(row, addendum)
                else:
                    next_cursor = 0

            users_done += 1
            update_stats()

        loading_bar.close()

    return action
