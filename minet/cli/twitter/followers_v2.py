import casanova
from twitter import TwitterHTTPError
from twitwi.constants_api_v2 import FOLLOWING_OR_FOLLOWERS_EXPANSIONS, FOLLOWING_OR_FOLLOWERS_PARAMS
from twitwi.constants import USER_FIELDS
from twitwi.normalizers import normalize_user
from twitwi.formatters import format_user_as_csv_row

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient
from minet.cli.twitter.utils import is_not_user_id

ITEMS_PER_PAGE = 1000
ADD_FIELDS = ['follower_id'] + USER_FIELDS[1:]


def twitter_followers_v2_action(cli_args):
    enricher = casanova.batch_enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=ADD_FIELDS
    )

    loading_bar = LoadingBar(
        desc='Retrieving users',
        unit='follower'
    )

    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key,
        api_version='2'
    )

    resuming_state = None

    if cli_args.resume:
        resuming_state = cli_args.output.pop_state()

    for row, user in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.print('Retrieving followers')
        loading_bar.inc('users')

        all_ids = []
        next_cursor = None
        result = None

        if resuming_state is not None and resuming_state.last_cursor:
            next_cursor = int(resuming_state.last_cursor)

        if is_not_user_id(user):
            loading_bar.die('The column given as argument doesn\'t contain user ids, you have probably given user screen names as argument instead. With --api-v2, you can only use user ids to retrieve followers.')

        client_kwargs = {'expansions': FOLLOWING_OR_FOLLOWERS_EXPANSIONS, 'params': FOLLOWING_OR_FOLLOWERS_PARAMS, 'max_results': ITEMS_PER_PAGE}

        while True:

            skip_in_output = None

            if resuming_state:
                skip_in_output = resuming_state.values_to_skip
                resuming_state = None

            try:
                result = client.call(route=['users', user, 'followers'], **client_kwargs)
            except TwitterHTTPError as e:

                # The user does not exist
                loading_bar.inc('users_not_found')
                break

            if result is not None and 'data' in result:
                batch = []

                for follower_metadata in result['data']:
                    normalized_follower = normalize_user(follower_metadata, v2=True)

                    addendum = format_user_as_csv_row(normalized_follower)
                    if skip_in_output and addendum[0] in skip_in_output:
                        continue
                    batch.append(addendum)

                loading_bar.update(len(result['data']))

                enricher.writebatch(row, batch, next_cursor or None)

                if 'next_token' in result['meta']:
                    next_cursor = result['meta']['next_token']
                    client_kwargs['pagination_token'] = next_cursor
                else:
                    break

            else:
                break

        loading_bar.inc('users')
