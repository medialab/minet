# =============================================================================
# Minet Twitter User Tweets CLI Action
# =============================================================================
#
# Logic of the `tw user-tweets` action.
#
import casanova
from twitwi import (
    TwitterWrapper,
    normalize_tweet,
    format_tweet_as_csv_row
)
from twitwi.constants import TWEET_FIELDS
from twitter import TwitterHTTPError

from minet.cli.utils import LoadingBar
from minet.twitter.constants import TWITTER_API_MAX_STATUSES_COUNT


def twitter_user_tweets_action(cli_args):

    wrapper = TwitterWrapper(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key
    )

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        keep=cli_args.select,
        add=TWEET_FIELDS
    )

    loading_bar = LoadingBar(
        'Retrieving tweets',
        total=cli_args.total,
        unit='tweet'
    )

    for row, user in enricher.cells(cli_args.column, with_rows=True):
        max_id = None

        loading_bar.update_stats(user=user)

        while True:
            if cli_args.ids:
                kwargs = {'user_id': user}
            else:
                kwargs = {'screen_name': user}

            kwargs['include_rts'] = not cli_args.exclude_retweets
            kwargs['count'] = TWITTER_API_MAX_STATUSES_COUNT
            kwargs['tweet_mode'] = 'extended'

            if max_id is not None:
                kwargs['max_id'] = max_id

            loading_bar.inc('calls')

            try:
                tweets = wrapper.call(['statuses', 'user_timeline'], **kwargs)
            except TwitterHTTPError as e:
                loading_bar.inc('errors')

                if e.e.code == 404:
                    loading_bar.print('Could not find user "%s"' % user)
                else:
                    loading_bar.print('An error happened when attempting to retrieve tweets from "%s"' % user)

                break

            if not tweets:
                break

            loading_bar.update(len(tweets))

            max_id = min(int(tweet['id_str']) for tweet in tweets) - 1

            for tweet in tweets:
                tweet = normalize_tweet(
                    tweet,
                    collection_source='api'
                )
                addendum = format_tweet_as_csv_row(tweet)

                enricher.writerow(row, addendum)

        loading_bar.inc('done')
