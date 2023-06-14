# =============================================================================
# Minet Twitter User Tweets CLI Action
# =============================================================================
#
# Logic of the `tw user-tweets` action.
#
from datetime import datetime
from twitwi import normalize_tweet, normalize_tweets_payload_v2, format_tweet_as_csv_row
from twitwi.constants import TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_PARAMS
from twitter import TwitterHTTPError

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.exceptions import FatalError
from minet.twitter.constants import TWITTER_API_MAX_STATUSES_COUNT
from minet.cli.twitter.utils import (
    is_not_user_id,
    is_probably_not_user_screen_name,
    with_twitter_client,
)

ITEMS_PER_PAGE = 100


@with_enricher_and_loading_bar(
    headers=TWEET_FIELDS,
    title="Retrieving user tweets",
    unit="users",
    nested=True,
    sub_unit="tweets",
)
@with_twitter_client()
def action(cli_args, client, enricher, loading_bar):
    for row, user in enricher.cells(cli_args.column, with_rows=True):
        with loading_bar.step(user):
            max_id = None

            min_date_reached = False

            kwargs = {}

            while True:
                if cli_args.v2:
                    if is_not_user_id(user):
                        raise FatalError(
                            "The column given as argument doesn't contain user ids, you have probably given user screen names as argument instead. With --v2, you can only use user ids to retrieve followers."
                        )

                    kwargs["max_results"] = ITEMS_PER_PAGE
                    kwargs["params"] = TWEET_PARAMS
                    kwargs["expansions"] = ",".join(TWEET_EXPANSIONS)

                    if cli_args.exclude_retweets:
                        kwargs["exclude"] = "retweets"
                    if cli_args.min_date:
                        utc_dt = datetime.fromtimestamp(cli_args.min_date).strftime(
                            "%Y-%m-%d"
                        )
                        kwargs["start_time"] = utc_dt + "T00:00:00Z"

                    try:
                        tweets = client.call(["users", user, "tweets"], **kwargs)
                    except TwitterHTTPError as e:
                        if e.e.code == 404:
                            loading_bar.print('Could not find user "%s"' % user)
                        else:
                            loading_bar.print(
                                'An error happened when attempting to retrieve tweets from "%s" (HTTP status %i)'
                                % (user, e.e.code)
                            )

                        break

                    try:
                        normalized_tweets = normalize_tweets_payload_v2(
                            tweets, locale=cli_args.timezone, collection_source="api"
                        )
                    except TypeError:
                        loading_bar.print(
                            'An error happened when attempting to retrieve tweets from "%s"'
                            % user
                        )
                        loading_bar.print(
                            'details: "%s"' % tweets["errors"][0]["detail"]
                        )
                        break

                    for normalized_tweet in normalized_tweets:
                        addendum = format_tweet_as_csv_row(normalized_tweet)
                        enricher.writerow(row, addendum)

                    if "next_token" in tweets["meta"]:
                        kwargs["pagination_token"] = tweets["meta"]["next_token"]
                    else:
                        break

                else:
                    if cli_args.ids:
                        if is_not_user_id(user):
                            raise FatalError(
                                "The column given as argument doesn't contain user ids, you have probably given user screen names as argument instead. \nTry removing --ids from the command."
                            )

                        kwargs = {"user_id": user}

                    else:
                        if is_probably_not_user_screen_name(user):
                            raise FatalError(
                                "The column given as argument probably doesn't contain user screen names, you have probably given user ids as argument instead. \nTry adding --ids to the command."
                            )
                            # force flag to add

                        kwargs = {"screen_name": user}

                    kwargs["include_rts"] = not cli_args.exclude_retweets
                    kwargs["count"] = TWITTER_API_MAX_STATUSES_COUNT
                    kwargs["tweet_mode"] = "extended"

                    if max_id is not None:
                        kwargs["max_id"] = max_id

                    try:
                        tweets = client.call(["statuses", "user_timeline"], **kwargs)
                    except TwitterHTTPError as e:
                        if e.e.code == 404:
                            loading_bar.print('Could not find user "%s"' % user)
                        else:
                            loading_bar.print(
                                'An error happened when attempting to retrieve tweets from "%s" (HTTP status %i)'
                                % (user, e.e.code)
                            )

                        break

                    if not tweets:
                        break

                    max_id = min(int(tweet["id_str"]) for tweet in tweets) - 1

                    for tweet in tweets:
                        tweet = normalize_tweet(
                            tweet, locale=cli_args.timezone, collection_source="api"
                        )
                        addendum = format_tweet_as_csv_row(tweet)

                        if cli_args.min_date:
                            if int(addendum[1]) < cli_args.min_date:
                                min_date_reached = True
                                break

                        enricher.writerow(row, addendum)
                        loading_bar.nested_advance()

                if min_date_reached:
                    break
