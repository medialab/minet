# =============================================================================
# Minet Twitter Tweet Count CLI Action
# =============================================================================
#
# Logic of the `tw tweet-count` action.
#
import casanova
from twitter import TwitterHTTPError

from minet.cli.utils import LoadingBar
from minet.cli.twitter.utils import validate_query_boundaries
from minet.twitter import TwitterAPIClient

ITEMS_PER_PAGE = 100

COUNT_FIELDS = ['tweet_count']
GRANULARIZED_COUNT_FIELDS = ['start_time', 'end_time', 'tweet_count']


def twitter_tweet_count_action(cli_args):
    validate_query_boundaries(cli_args)

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
        add=GRANULARIZED_COUNT_FIELDS if cli_args.granularity is not None else COUNT_FIELDS,
        total=cli_args.total
    )

    loading_bar = LoadingBar(
        'Counting tweets',
        total=enricher.total,
        unit='query',
        unit_plural='queries'
    )

    for row, query in enricher.cells(cli_args.query, with_rows=True):

        kwargs = {'query': query}

        loading_bar.print('Counting tweets for "%s"' % query)

        # Because we are greedy, we want stuff from the beginning of Twitter
        if cli_args.academic and not cli_args.start_time:
            kwargs['start_time'] = '2006-01-01T00:00:00Z'

        if cli_args.start_time:
            kwargs['start_time'] = cli_args.start_time
        if cli_args.end_time:
            kwargs['end_time'] = cli_args.end_time
        if cli_args.since_id:
            kwargs['since_id'] = cli_args.since_id
        if cli_args.until_id:
            kwargs['until_id'] = cli_args.until_id

        kwargs['granularity'] = cli_args.granularity or 'day'

        route = ['tweets', 'counts', 'all'] if cli_args.academic else ['tweets', 'counts', 'recent']

        total_count = 0

        while True:
            try:
                result = client.call(route, **kwargs)
                loading_bar.inc('calls')
            except TwitterHTTPError as e:
                loading_bar.inc('errors')

                if e.e.code == 404:
                    enricher.writerow(row)
                else:
                    raise e

                continue

            for count in result['data']:
                total_count += count['tweet_count']

                if cli_args.granularity is not None:
                    addendum = [count['start'], count['end'], count['tweet_count']]
                    enricher.writerow(row, addendum)

            if 'next_token' in result['meta']:
                kwargs['next_token'] = result['meta']['next_token']
            else:
                break

        loading_bar.update()

        if cli_args.granularity is None:
            enricher.writerow(row, [total_count])
