# =============================================================================
# Minet Twitter Tweet Search CLI Action
# =============================================================================
#
# Logic of the `tw tweet-search` action.
#
import casanova
from twitwi import (
    normalize_tweets_payload_v2,
    format_tweet_as_csv_row
)
from twitwi.constants import TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_PARAMS
from twitter import TwitterHTTPError

from minet.cli.utils import LoadingBar
from minet.twitter import TwitterAPIClient

ITEMS_PER_PAGE = 100


def twitter_tweet_search_action(cli_args):
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
        add=TWEET_FIELDS,
        total=cli_args.total
    )

    loading_bar = LoadingBar(
        'Retrieving tweets',
        total=enricher.total,
        unit='tweet'
    )

    for row, query in enricher.cells(cli_args.query, with_rows=True):

        kwargs = {'query': query, 'max_results': ITEMS_PER_PAGE, 'sort_order': 'recency', 'expansions': ','.join(TWEET_EXPANSIONS), 'params': TWEET_PARAMS}

        loading_bar.print('Searching for "%s"' % query)
        loading_bar.inc('queries')

        already_seen_tweets = set()

        if cli_args.start_time and cli_args.end_time:
            if cli_args.end_time < cli_args.start_time:
                loading_bar.die('end-time should be greater than start-time.')

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

        while True:

            if cli_args.academic:
                try:
                    result = client.call(['tweets', 'search', 'all'], **kwargs)
                except TwitterHTTPError as e:
                    loading_bar.inc('errors')

                    if e.e.code == 404:
                        enricher.writerow(row)
                    else:
                        raise e

                    continue

            else:
                try:
                    result = client.call(['tweets', 'search', 'recent'], **kwargs)
                except TwitterHTTPError as e:
                    loading_bar.inc('errors')

                    if e.e.code == 404:
                        enricher.writerow(row)
                    else:
                        raise e

                    continue

            if result['meta']['result_count'] == 0 and 'next_token' in result['meta']:
                loading_bar.print(result)
                kwargs['next_token'] = result['meta']['next_token']
                continue

            normalized_tweets = normalize_tweets_payload_v2(result, collection_source='api')

            for normalized_tweet in normalized_tweets:
                if normalized_tweet['id'] in already_seen_tweets:
                    continue

                loading_bar.update()

                addendum = format_tweet_as_csv_row(normalized_tweet)
                enricher.writerow(row, addendum)
                already_seen_tweets.add(normalized_tweet['id'])

            if 'next_token' in result['meta']:
                kwargs['next_token'] = result['meta']['next_token']
            else:
                break
