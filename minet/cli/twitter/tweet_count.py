# =============================================================================
# Minet Twitter Tweet Count CLI Action
# =============================================================================
#
# Logic of the `tw tweet-count` action.
#
import casanova
from twitter import TwitterHTTPError

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient

ITEMS_PER_PAGE = 100
TWEETS_COUNT_FIELDS = [
    'start_time',
    'end_time',
    'tweet_count',
    'total_count'
]


def twitter_tweet_count_action(cli_args):
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
        add=TWEETS_COUNT_FIELDS,
        total=cli_args.total
    )

    loading_bar = LoadingBar(
        'Retrieving tweet count',
        total=enricher.total,
        unit='query'
    )

    for row, query in enricher.cells(cli_args.query, with_rows=True):

        kwargs = {'query': query, 'granularity': 'day'}

        loading_bar.print('Counting tweets for "%s"' % query)
        loading_bar.inc('queries')

        if cli_args.start_time and cli_args.end_time:
            if cli_args.end_time < cli_args.start_time:
                loading_bar.die('The end time should be greater than the start time.')

        if cli_args.since_id and cli_args.until_id:
            if cli_args.until_id < cli_args.since_id:
                loading_bar.die('until-id should be greater than since-id')

        if cli_args.start_time:
            kwargs['start_time'] = cli_args.start_time
        if cli_args.end_time:
            kwargs['end_time'] = cli_args.end_time
        if cli_args.since_id:
            kwargs['since_id'] = cli_args.since_id
        if cli_args.until_id:
            kwargs['until_id'] = cli_args.until_id

        if cli_args.granularity:
            kwargs['granularity'] = cli_args.granularity

        if cli_args.academic:
            total_count = 0
            while True:
                try:
                    result = client.call(['tweets', 'counts', 'all'], **kwargs)
                except TwitterHTTPError as e:
                    loading_bar.inc('errors')

                    if e.e.code == 404:
                        enricher.writerow(row)
                    else:
                        raise e

                    continue

                for count in result['data']:
                    total_count += result['meta']['total_tweet_count']
                    addendum = [count['start'], count['end'], count['tweet_count'], total_count]
                    enricher.writerow(row, addendum)

                if 'next_token' in result['meta']:
                    kwargs['next_token'] = result['meta']['next_token']
                else:
                    break

        else:
            try:
                result = client.call(['tweets', 'counts', 'recent'], **kwargs)
            except TwitterHTTPError as e:
                loading_bar.inc('errors')

                if e.e.code == 404:
                    enricher.writerow(row)
                else:
                    raise e

                continue

            for count in result['data']:
                addendum = [count['start'], count['end'], count['tweet_count'], result['meta']['total_tweet_count']]
                enricher.writerow(row, addendum)
