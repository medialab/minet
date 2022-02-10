# =============================================================================
# Minet Twitter Retweeters CLI Action
# =============================================================================
#
# Logic of the `tw retweeters` action.
#
import casanova
from twitter import TwitterHTTPError

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient

ITEMS_PER_PAGE = 100
CSV_HEADERS = [
    'retweeter_id',
    'retweeter_screen_name',
    'retweeter_name'
]


def twitter_retweeters_action(cli_args):
    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key,
        api_version='2'
    )

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=CSV_HEADERS,
        total=cli_args.total
    )

    loading_bar = LoadingBar(
        'Retrieving retweeters',
        total=enricher.total,
        unit=' users'
    )

    for row, tweet in enricher.cells(cli_args.column, with_rows=True):
        loading_bar.inc('tweets')
        kwargs = {'max_results': ITEMS_PER_PAGE}

        while True:
            try:
                result = client.call(['tweets', tweet, 'retweeted_by'], **kwargs)
            except TwitterHTTPError as e:
                loading_bar.inc('errors')

                if e.e.code == 404:
                    enricher.writerow(row)
                else:
                    raise e

                continue

            if 'data' not in 'result' and result['meta']['result_count'] == 0:
                break

            for user in result['data']:
                id = user['id']
                screen_name = user['username']
                name = user['name']
                enricher.writerow(row, [id, screen_name, name])
                loading_bar.update()

            if 'next_token' in result['meta']:
                kwargs['pagination_token'] = result['meta']['next_token']
            else:
                break
