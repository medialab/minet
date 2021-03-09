# =============================================================================
# Minet Twitter Users CLI Action
# =============================================================================
#
# Logic of the `tw users` action.
#
import casanova
from twitwi import (
    TwitterWrapper,
    normalize_user,
    format_user_as_csv_row
)
from twitwi.constants import USER_FIELDS
from tqdm import tqdm
from ebbe import as_chunks


def twitter_users_action(namespace, output_file):

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
        add=USER_FIELDS
    )

    loading_bar = tqdm(
        desc='Retrieving users',
        dynamic_ncols=True,
        total=namespace.total,
        unit=' user'
    )

    for chunk in as_chunks(enricher.cells(100, namespace.column, with_rows=True)):
        users = ','.join(row[1] for row in chunk)

        if namespace.ids:
            wrapper_args = {'user_id': users}
            key = 'id'
        else:
            wrapper_args = {'screen_name': users}
            key = 'screen_name'

        result = wrapper.call(['users', 'lookup'], **wrapper_args)

        if result is not None:
            indexed_result = {}

            for user in result:
                user = normalize_user(user)
                user_row = format_user_as_csv_row(user)
                indexed_result[user[key]] = user_row

            for row, user in chunk:
                user_row = indexed_result.get(user)

                enricher.writerow(row, user_row)

        loading_bar.update(len(chunk))

    loading_bar.close()
