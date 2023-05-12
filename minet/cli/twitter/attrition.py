# =============================================================================
# Minet Twitter Attrition CLI Action
# =============================================================================
#
# Logic of the `tw attrition` action.
#
from twitter import TwitterHTTPError
from ebbe import getpath, as_chunks
from ural.twitter import TwitterTweet, parse_twitter_url

from minet.cli.utils import with_enricher_and_loading_bar
from minet.cli.exceptions import InvalidArgumentsError, FatalError
from minet.cli.twitter.utils import (
    is_not_user_id,
    is_probably_not_user_screen_name,
    with_twitter_client,
)

ATTRITION_ADDITIONAL_HEADERS = ["tweet_current_status"]


@with_enricher_and_loading_bar(
    headers=ATTRITION_ADDITIONAL_HEADERS,
    title="Retrieving attrition reason",
    unit="tweet",
)
@with_twitter_client()
def action(cli_args, client, enricher, loading_bar):
    user_cache = {}
    result = None

    if cli_args.column not in enricher.headers:
        raise InvalidArgumentsError(
            'Could not find the "%s" column containing the tweet ids in the given CSV file.'
            % cli_args.column
        )

    if cli_args.user:
        if not cli_args.has_dummy_csv:
            if cli_args.user not in enricher.headers:
                raise InvalidArgumentsError(
                    'Could not find the "%s" column containing the user ids in the given CSV file.'
                    % cli_args.user
                )

            user_column = cli_args.user
            user_pos = enricher.headers[user_column]

    if cli_args.retweeted_id and cli_args.retweeted_id not in enricher.headers:
        raise InvalidArgumentsError(
            'Could not find the "%s" column containing the retweeted ids in the given CSV file.'
            % cli_args.retweeted_id
        )

    def cells():
        for row, cell in enricher.cells(cli_args.column, with_rows=True):
            if cell == "":
                tweet = None
                user = None

            else:
                parsed = parse_twitter_url(cell)

                if parsed is None:
                    tweet = cell
                    user = None
                elif isinstance(parsed, TwitterTweet):
                    tweet = parsed.id
                    user = parsed.user_screen_name
                else:
                    tweet = None
                    user = None

                if cli_args.user:
                    if cli_args.has_dummy_csv:
                        user = cli_args.user

                    else:
                        if row[user_pos] == "":
                            user = None
                        else:
                            user = row[user_pos]

                    if cli_args.ids:
                        if is_not_user_id(user):
                            raise FatalError(
                                "The column given as argument doesn't contain user ids, you have probably given user screen names as argument instead. \nTry removing --ids from the command."
                            )

                    else:
                        if is_probably_not_user_screen_name(user):
                            raise FatalError(
                                "The column given as argument probably doesn't contain user screen names, you have probably given user ids as argument instead. \nTry adding --ids to the command."
                            )
                            # force flag to add

            yield row, tweet, user

    for chunk in as_chunks(100, cells()):
        available_tweets = set()

        # WARNING: if each tweet in chunk is None, the client calls the API with empty tweets list
        tweets = ",".join(row[1] for row in chunk if row[1] is not None)
        kwargs = {"_id": tweets}

        # First we need to query a batch of tweet ids at once to figure out
        # whether they are still available or not
        try:
            result = client.call(["statuses", "lookup"], **kwargs)

        except TwitterHTTPError as e:
            loading_bar.inc_stat("errors", style="error")
            loading_bar.advance(len(chunk))
            raise e

        for tw in result:
            available_tweets.add(tw["id_str"])

        for row, tweet, user in chunk:
            loading_bar.advance()

            if tweet is None:
                enricher.writerow(row)
                loading_bar.print(
                    "The url or id given doesn't correspond to a tweet : %s"
                    % row[enricher.headers[cli_args.column]]
                )
                continue

            if tweet in available_tweets:
                current_tweet_status = "available_tweet"
                enricher.writerow(row, [current_tweet_status])
                continue

            # If tweet is not available, we will query once more to find out
            # what the reason for its unavailability is

            client_args = {"_id": tweet}

            current_tweet_status = "unknown"

            result_tweet = None

            try:
                result_tweet = client.call(["statuses", "show"], **client_args)

            except TwitterHTTPError as e:
                error_code = getpath(e.response_data, ["errors", 0, "code"], "")

                if e.e.code == 403 and error_code == 63:
                    current_tweet_status = "suspended_user"

                elif e.e.code == 403 and error_code == 179:
                    current_tweet_status = "protected_user"

                elif e.e.code == 404 and (error_code == 144 or error_code == 34):
                    current_tweet_status = "user_or_tweet_deleted"

                elif e.e.code == 404 and (error_code == 421 or error_code == 422):
                    current_tweet_status = "censored_tweet"

                elif e.e.code == 401 and (error_code == 136):
                    current_tweet_status = "blocked_by_tweet_author"

                else:
                    raise e

            # This could happen in a case where you've been blocked by the tweet's author.
            # This is because the client uses 2 different methods to call the API, one linked to a user and one to an app.
            # One can be blocked and not the other.
            if result_tweet is not None:
                current_tweet_status = "available_tweet"

            if (
                current_tweet_status == "user_or_tweet_deleted"
                or current_tweet_status == "unknown"
            ):
                if user is not None:
                    if user in user_cache:
                        if user_cache[user] == "user_ok":
                            current_tweet_status = "unavailable_tweet"

                        else:
                            current_tweet_status = user_cache[user]

                    else:
                        if cli_args.ids:
                            c_args = {"user_id": user}
                        else:
                            c_args = {"screen_name": user}

                        try:
                            client.call(["users", "show"], **c_args)

                        except TwitterHTTPError as e:
                            error_code = getpath(
                                e.response_data, ["errors", 0, "code"], ""
                            )
                            if e.e.code == 404 and error_code == 50:
                                if cli_args.ids:
                                    current_tweet_status = "deactivated_user"
                                    user_cache[user] = "deactivated_user"
                                else:
                                    current_tweet_status = "deactivated_or_renamed_user"
                                    user_cache[user] = "deactivated_or_renamed_user"

                            else:
                                current_tweet_status = "unavailable_tweet"

                        else:
                            user_cache[user] = "user_ok"
                            current_tweet_status = "unavailable_tweet"

                # Sometimes, the unavailable tweet is a retweet, in which
                # case we need to enquire about the original tweet to find
                # a reason for the tweet's unavailability
                if cli_args.retweeted_id:
                    if (
                        current_tweet_status == "unavailable_tweet"
                        or current_tweet_status == "unknown"
                    ):
                        if cli_args.has_dummy_csv:
                            original_tweet = cli_args.retweeted_id
                        else:
                            original_id_pos = enricher.headers[cli_args.retweeted_id]
                            original_tweet = row[original_id_pos]

                        client_arg = {"_id": original_tweet}
                        result_retweet = None

                        if original_tweet:
                            try:
                                result_retweet = client.call(
                                    ["statuses", "show"], **client_arg
                                )

                            except TwitterHTTPError as e:
                                error_code = getpath(
                                    e.response_data, ["errors", 0, "code"], ""
                                )
                                if e.e.code == 403 and error_code == 63:
                                    current_tweet_status = "suspended_retweeted_user"

                                elif e.e.code == 403 and error_code == 179:
                                    current_tweet_status = "protected_retweeted_user"

                                elif e.e.code == 404 and (
                                    error_code == 144 or error_code == 34
                                ):
                                    current_tweet_status = "unavailable_retweeted_tweet"

                                elif e.e.code == 404 and (
                                    error_code == 421 or error_code == 422
                                ):
                                    current_tweet_status = "censored_retweeted_tweet"

                                elif e.e.code == 401 and (error_code == 136):
                                    current_tweet_status = (
                                        "blocked_by_original_tweet_author"
                                    )

                                else:
                                    raise e

                            if result_retweet is not None:
                                current_tweet_status = "unavailable_retweet"

                if current_tweet_status == "unknown":
                    current_tweet_status = "unavailable_tweet"

            enricher.writerow(row, [current_tweet_status])
