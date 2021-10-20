# =============================================================================
# Minet Twitter User Tweets CLI Action
# =============================================================================
#
# Logic of the `tw user-tweets` action.
#
import casanova
from twitwi import (
    normalize_tweet,
    format_tweet_as_csv_row
)
from twitwi.constants import TWEET_FIELDS
from twitter import TwitterHTTPError

from minet.cli.utils import LoadingBar
from minet.twitter.constants import TWITTER_API_MAX_STATUSES_COUNT
from minet.twitter import TwitterAPIClient
from minet.cli.twitter.utils import is_not_user_id, is_probably_not_user_screen_name


def twitter_user_tweets_action(cli_args):

    client = TwitterAPIClient(
        cli_args.access_token,
        cli_args.access_token_secret,
        cli_args.api_key,
        cli_args.api_secret_key
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
        unit='user'
    )

    for row, user in enricher.cells(cli_args.column, with_rows=True):
        max_id = None

        loading_bar.update_stats(user=user)

        while True:
            if cli_args.ids:
                if is_not_user_id(user):
                    loading_bar.die('The column given as argument doesn\'t contain user ids, you have probably given user screen names as argument instead. \nTry removing --ids from the command.')

                kwargs = {'user_id': user}

            else:
                if is_probably_not_user_screen_name(user):
                    loading_bar.die('The column given as argument probably doesn\'t contain user screen names, you have probably given user ids as argument instead. \nTry adding --ids to the command.')
                    # force flag to add

                kwargs = {'screen_name': user}

            kwargs['include_rts'] = not cli_args.exclude_retweets
            kwargs['count'] = TWITTER_API_MAX_STATUSES_COUNT
            kwargs['tweet_mode'] = 'extended'

            if max_id is not None:
                kwargs['max_id'] = max_id

            loading_bar.inc('calls')

            try:
                tweets = client.call(['statuses', 'user_timeline'], **kwargs)
            except TwitterHTTPError as e:
                loading_bar.inc('errors')

                if e.e.code == 404:
                    loading_bar.print('Could not find user "%s"' % user)
                else:
                    loading_bar.print('An error happened when attempting to retrieve tweets from "%s" (HTTP status %i)' % (user, e.e.code))

                break

            if not tweets:
                break

            loading_bar.inc('tweets', len(tweets))

            max_id = min(int(tweet['id_str']) for tweet in tweets) - 1

            min_date_reached = False

            for tweet in tweets:
                tweet = normalize_tweet(
                    tweet,
                    collection_source='api'
                )
                addendum = format_tweet_as_csv_row(tweet)

                if cli_args.min_date:
                    if int(addendum[1]) < cli_args.min_date:
                        min_date_reached = True
                        break

                enricher.writerow(row, addendum)

            if min_date_reached:
                break

        loading_bar.update()
