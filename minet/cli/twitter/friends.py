# =============================================================================
# Minet Twitter Friends CLI Action
# =============================================================================
#
# Logic of the `tw friends` action.
#
from minet.cli.twitter.utils import make_twitter_action

REPORT_HEADERS = [
    'friends_id'
]

twitter_friends_action = make_twitter_action(
    method_name='friends',
    csv_headers=REPORT_HEADERS
)


# def twitter_friends_action(namespace, output_file):

#     TWITTER = {
#         'access_token': namespace.access_token,
#         'access_token_secret': namespace.access_token_secret,
#         'api_key': namespace.api_key,
#         'api_secret_key': namespace.api_secret_key
#     }

#     wrapper = TwitterWrapper(TWITTER)

#     enricher = casanova.enricher(
#         namespace.file,
#         output_file,
#         keep=namespace.select,
#         add=REPORT_HEADERS
#     )

#     loading_bar = tqdm(
#         desc='Retrieving ids',
#         dynamic_ncols=True,
#         total=namespace.total,
#         unit=' line'
#     )

#     for row, user_id in enricher.cells(namespace.column, with_rows=True):
#         all_ids = []
#         next_cursor = -1
#         result = None

#         wrapper_args = {'user_id': user_id}

#         while next_cursor != 0:
#             wrapper_args['cursor'] = next_cursor
#             result = wrapper.call('friends.ids', wrapper_args)

#             if result is not None:
#                 all_ids = result.get('ids', [])
#                 next_cursor = result.get('next_cursor', 0)

#                 for friend_id in all_ids:
#                     enricher.writerow(row, [friend_id])
#             else:
#                 next_cursor = 0

#         loading_bar.update()

#     loading_bar.close()
