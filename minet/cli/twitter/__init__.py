# =============================================================================
# Minet Twitter CLI Action
# =============================================================================
#
# Logic of the `tw` action.
#
from casanova import RowCountResumer, BatchResumer

from minet.cli.argparse import (
    command,
    subcommand,
    ConfigAction,
    TimezoneType,
    TimestampType,
)
from minet.cli.exceptions import InvalidArgumentsError

TWITTER_API_COMMON_ARGUMENTS = [
    {
        "flag": "--api-key",
        "help": "Twitter API key.",
        "rc_key": ["twitter", "api_key"],
        "action": ConfigAction,
    },
    {
        "flag": "--api-secret-key",
        "help": "Twitter API secret key.",
        "rc_key": ["twitter", "api_secret_key"],
        "action": ConfigAction,
    },
    {
        "flag": "--access-token",
        "help": "Twitter API access token.",
        "rc_key": ["twitter", "access_token"],
        "action": ConfigAction,
    },
    {
        "flag": "--access-token-secret",
        "help": "Twitter API access token secret.",
        "rc_key": ["twitter", "access_token_secret"],
        "action": ConfigAction,
    },
]

V2_ARGUMENT = {
    "flag": "--v2",
    "help": "Whether to use latest Twitter API v2 rather than v1.1.",
    "action": "store_true",
}

IDS_ARGUMENT = {
    "flag": "--ids",
    "help": "Whether your users are given as ids rather than screen names.",
    "action": "store_true",
}

ACADEMIC_ARGUMENT = {
    "flag": "--academic",
    "help": "Flag to add if you want to use your academic research access (in order to search the complete history of public tweets).",
    "action": "store_true",
}

COMMON_V2_SEARCH_ARGUMENTS = [
    {
        "flag": "--since-id",
        "help": "Will return tweets with ids that are greater than the specified id. Takes precedence over --start-time.",
        "type": int,
    },
    {
        "flag": "--until-id",
        "help": "Will return tweets that are older than the tweet with the specified id.",
        "type": int,
    },
    {
        "flag": "--start-time",
        "help": "The oldest UTC stamp from which the tweets will be provided. The date should have the format : YYYY-MM-DDTHH:mm:ssZ",
    },
    {
        "flag": "--end-time",
        "help": "The UTC stamp to which the tweets will be provided. The date should have the format : YYYY-MM-DDTHH:mm:ssZ",
    },
]


def check_credentials(cli_args):

    # Credentials are required to be able to access the API
    if (
        not cli_args.api_key
        or not cli_args.api_secret_key
        or not cli_args.access_token
        or not cli_args.access_token_secret
    ):
        raise InvalidArgumentsError(
            [
                "Full credentials are required to access Twitter API.",
                "You can provide them using various CLI arguments:",
                "    --api-key",
                "    --api-secret-key",
                "    --access-token",
                "    --access-token-secret",
            ]
        )


def twitter_api_subcommand(*args, arguments=[], **kwargs):
    return subcommand(
        *args,
        arguments=arguments + TWITTER_API_COMMON_ARGUMENTS,
        resolve=check_credentials,
        **kwargs
    )


TWITTER_ATTRITION_SUBCOMMAND = twitter_api_subcommand(
    "attrition",
    "minet.cli.twitter.attrition",
    title="Minet Twitter Attrition Command",
    description="""
        Using Twitter API to find whether batches of tweets are still
        available today and if they aren't, attempt to find a reason why.

        This command relies on tweet ids or tweet urls. We recommand to add `--user` and
        the tweet's user id to the command if you can, as more information can
        be obtained when the user id (or the full url) is known.

        The same can be said about retweet information and the `--retweeted-id` flag.

        The command will output a report similar to the input file and
        containing an additional column named "current_tweet_status" that can take
        the following values:

            - "available_tweet": tweet is still available.
            - "user_or_tweet_deleted": tweet was deleted or its author was deactivated. To know whether it is one or the other reason
                                        for unavailability that is the right one, add --user to the command.
            - "suspended_user": tweet cannot be found because its user is suspended.
            - "deactivated_user": tweet cannot be found because its user is deactivated.
            - "deactivated_or_renamed_user": tweet cannot be found because its user is either deactivated or changed its screen name
                                                (only when using tweet urls or tweet ids and screen names instead of user ids).
            - "protected_user": tweet cannot be found because its user is protected.
            - "censored_tweet": tweet is unavailable because it was consored by Twitter.
            - "blocked_by_tweet_author": tweet cannot be found because you were blocked by its author.
            - "unavailable_tweet": tweet is not available, which means it was
                                    deleted by its user.
            - "unavailable_retweet": retweet is not available, meaning that the user
                                        cancelled their retweet.
            - "unavailable_retweeted_tweet": the retweeted tweet is unavailable,
                                                meaning it was either deleted by its original
                                                user or the original user was deactivated.
            - "censored_retweeted_tweet": the original tweet was censored by Twitter, making the retweet unavailable.
            - "protected_retweeted_user": tweet cannot be found because it is a retweet of a protected user.
            - "suspended_retweeted_user": tweet cannot be found because it is a retweet of a suspended user.
            - "blocked_by_original_tweet_author": tweet cannot be found because it is a retweet of a user who blocked you.
    """,
    epilog="""
        examples:

        . Finding out if tweets in a CSV files are still available or not using tweet ids:
            $ minet tw attrition tweet_url deleted_tweets.csv > attrition-report.csv

        . Finding out if tweets are still available or not using tweet & user ids:
            $ minet tw attrition tweet_id deleted_tweets.csv --user user_id --ids > attrition-report.csv
    """,
    variadic_input={
        "dummy_column": "tweet_url_or_id",
        "item_label": "tweet url or id",
        "item_label_plural": "tweet urls or ids",
    },
    resumer=RowCountResumer,
    select=True,
    total=True,
    arguments=[
        {
            "flag": "--user",
            "help": "Name of the column containing the tweet's author (given as ids or screen names). This is useful to have more information on a tweet's unavailability.",
        },
        {
            "flag": "--retweeted-id",
            "help": "Name of the column containing the ids of the original tweets in case the tweets no longer available were retweets.",
        },
        IDS_ARGUMENT,
    ],
)

TWITTER_FOLLOWERS_SUBCOMMAND = twitter_api_subcommand(
    "followers",
    "minet.cli.twitter.followers",
    title="Minet Twitter Followers Command",
    description="""
        Retrieve followers, i.e. followed users, of given user.
    """,
    epilog="""
        examples:

        . Getting followers of a list of user:
            $ minet tw followers screen_name users.csv > followers.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "Twitter account screen name or id",
        "item_label_plural": "Twitter account screen names or ids",
    },
    resumer=BatchResumer,
    resumer_kwargs=lambda args: ({"value_column": args.column}),
    select=True,
    total=True,
    arguments=[
        IDS_ARGUMENT,
        V2_ARGUMENT,
    ],
)

TWITTER_FRIENDS_SUBCOMMAND = twitter_api_subcommand(
    "friends",
    "minet.cli.twitter.friends",
    title="Minet Twitter Friends Command",
    description="""
        Retrieve friends, i.e. followed users, of given user.
    """,
    epilog="""
        examples:

        . Getting friends of a list of user:
            $ minet tw friends screen_name users.csv > friends.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "Twitter account screen name or id",
        "item_label_plural": "Twitter account screen names or ids",
    },
    resumer=BatchResumer,
    resumer_kwargs=lambda args: ({"value_column": args.column}),
    select=True,
    total=True,
    arguments=[
        IDS_ARGUMENT,
        V2_ARGUMENT,
    ],
)

TWITTER_LIST_FOLLOWERS_SUBCOMMAND = twitter_api_subcommand(
    "list-followers",
    "minet.cli.twitter.list_followers",
    title="Minet Twitter List Followers Command",
    description="""
        Retrieve followers of given list using Twitter API v2.
    """,
    epilog="""
        examples:

        . Getting followers of a list of lists:
            $ minet tw list-followers id lists.csv > followers.csv
    """,
    variadic_input={
        "dummy_column": "list",
        "item_label": "Twitter list id or url",
        "item_label_plural": "Twitter list ids or urls",
    },
    select=True,
    total=True,
)

TWITTER_LIST_MEMBERS_SUBCOMMAND = twitter_api_subcommand(
    "list-members",
    "minet.cli.twitter.list_members",
    title="Minet Twitter List Members Command",
    description="""
        Retrieve members of given list using Twitter API v2.
    """,
    epilog="""
        examples:

        . Getting members of a list of lists:
            $ minet tw list-members id lists.csv > members.csv
    """,
    variadic_input={
        "dummy_column": "list",
        "item_label": "Twitter list id or url",
        "item_label_plural": "Twitter list ids or urls",
    },
    select=True,
    total=True,
)

TWITTER_RETWEETERS_SUBCOMMAND = twitter_api_subcommand(
    "retweeters",
    "minet.cli.twitter.retweeters",
    title="Minet Twitter Retweeters Command",
    description="""
        Retrieve retweeters of given tweet using Twitter API v2.
    """,
    epilog="""
        examples:

        . Getting the users who retweeted a list of tweets:
            $ minet tw retweeters tweet_id tweets.csv > retweeters.csv
    """,
    variadic_input={"dummy_column": "tweet_id", "item_label": "tweet id"},
    select=True,
    total=True,
)

TWITTER_SCRAPE_SUBCOMMAND = subcommand(
    "scrape",
    "minet.cli.twitter.scrape",
    title="Minet Twitter Scrape Command",
    description="""
        Scrape Twitter's public facing search API to collect tweets or users.

        Be sure to check Twitter's advanced search to check what kind of
        operators you can use to tune your queries (time range, hashtags,
        mentions, boolean etc.):
        https://twitter.com/search-advanced?f=live

        Useful operators include "since" and "until" to search specific
        time ranges like so: "since:2014-01-01 until:2017-12-31".

        BEWARE: the web search results seem to become inconsistent when
        queries return vast amounts of tweets. In which case you are
        strongly advised to segment your queries using temporal filters.
    """,
    epilog="""
        examples:

        . Collecting the latest 500 tweets of a given Twitter user:
            $ minet tw scrape tweets "from:@jack" --limit 500 > tweets.csv

        . Collecting the tweets from multiple Twitter queries listed in a CSV file:
            $ minet tw scrape tweets query queries.csv > tweets.csv

        . Templating the given CSV column to query tweets by users:
            $ minet tw scrape tweets user users.csv --query-template 'from:@{value}' > tweets.csv

        . Tip: You can add a "OR @aNotExistingHandle" to your query to avoid searching
          for your query terms in usernames or handles.
          Note that this is a temporary hack which might stop working at any time so be
          sure to double check before relying on this trick.
          For more information see the related discussion here:
          https://webapps.stackexchange.com/questions/127425/how-to-exclude-usernames-and-handles-while-searching-twitter

            $ minet tw scrape tweets "keyword OR @anObviouslyNotExistingHandle"

        . Collecting users with "adam" in their user_name or user_description:
            $ minet tw scrape users adam > users.csv
    """,
    select=True,
    variadic_input={"dummy_column": "query", "item_label_plural": "queries"},
    arguments=[
        {
            "name": "items",
            "help": "What to scrape. Currently only allows for `tweets` or `users`.",
            "choices": ["tweets", "users"],
        },
        {
            "flag": "--include-refs",
            "help": "Whether to emit referenced tweets (quoted, retweeted & replied) in the CSV output. Note that it consumes a memory proportional to the total number of unique tweets retrieved.",
            "action": "store_true",
        },
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of tweets or users to collect per query.",
            "type": int,
        },
        {
            "flag": "--query-template",
            "help": "Query template. Can be useful for instance to change a column of twitter user screen names into from:@user queries.",
        },
    ],
)

TWITTER_TWEET_COUNT_SUBCOMMAND = twitter_api_subcommand(
    "tweet-count",
    "minet.cli.twitter.tweet_count",
    title="Minet Twitter Tweets Count Command",
    description="""
        Count the number of tweets matching the given query using Twitter's
        latest API v2. The count's granularity can be at the level of tweets
        per day, per hour, or per minute.

        This will only return result for the last 8 days only, unless
        you have Academic Research access in which case you
        can use the --academic flag to retrieve the full count.

        Be advised that, for now, results are returned unordered
        by Twitter's API if you choose a time granularity for the
        results.
    """,
    epilog="""
        examples:

        . Counting tweets using "cancer" as a query:
            $ minet tw tweet-count cancer

        . Running multiple queries in series:
            $ minet tw tweet-count query queries.csv > counts.csv

        . Number of tweets matching the query per day:
            $ minet tw tweet-count "query" --granularity day > counts.csv
    """,
    variadic_input={"dummy_column": "query", "item_label_plural": "queries"},
    select=True,
    total=True,
    arguments=[
        {
            "flag": "--granularity",
            "help": "Granularity used to group the data by. Defaults to day.",
            "choices": ["minute", "hour", "day"],
        },
        *COMMON_V2_SEARCH_ARGUMENTS,
        ACADEMIC_ARGUMENT,
    ],
)

TWITTER_TWEET_DATE_SUBCOMMAND = subcommand(
    "tweet-date",
    "minet.cli.twitter.tweet_date",
    title="Minet Twitter Tweet Date Command",
    description="""
        Getting timestamp and date from tweet url or id.
    """,
    epilog="""
        examples:

            $ minet tw tweet-date url tweets.csv --timezone 'Europe/Paris'> tweets_timestamp_date.csv
    """,
    variadic_input={
        "dummy_column": "tweet",
        "item_label": "tweet url or id",
        "item_label_plural": "tweet urls or ids",
    },
    select=True,
    arguments=[
        {
            "flag": "--timezone",
            "help": "Timezone for the date, for example 'Europe/Paris'. Default to UTC.",
            "type": TimezoneType(),
        }
    ],
)

TWITTER_TWEET_SEARCH_SUBCOMMAND = twitter_api_subcommand(
    "tweet-search",
    "minet.cli.twitter.tweet_search",
    title="Minet Twitter Tweets Search Command",
    description="""
        Search Twitter tweets using API v2.

        This will only return the last 8 days of results maximum per query (unless you have Academic Research access).

        To search the full archive of public tweets, use --academic if you have academic research access.
    """,
    epilog="""
        examples:

        . Searching tweets using "cancer" as a query:
            $ minet tw tweet-search cancer > tweets.csv

        . Running multiple queries in series:
            $ minet tw tweet-search query queries.csv > tweets.csv
    """,
    variadic_input={"dummy_column": "query", "item_label_plural": "queries"},
    select=True,
    total=True,
    arguments=[
        *COMMON_V2_SEARCH_ARGUMENTS,
        ACADEMIC_ARGUMENT,
        {
            "flag": "--sort-order",
            "help": 'How to sort retrieved tweets. Defaults to "recency".',
            "choices": ["recency", "relevancy"],
            "default": "recency",
        },
    ],
)

TWITTER_TWEETS_SUBCOMMAND = twitter_api_subcommand(
    "tweets",
    "minet.cli.twitter.tweets",
    title="Minet Twitter Tweets Command",
    description="""
        Collecting tweet metadata from the given tweet ids, using the API.
    """,
    epilog="""
        examples:

        . Getting metadata from tweets in a CSV file:
            $ minet tw tweets tweet_id tweets.csv > tweets_metadata.csv
    """,
    variadic_input={"dummy_column": "tweet_id", "item_label": "tweet id"},
    resumer=RowCountResumer,
    select=True,
    total=True,
    arguments=[V2_ARGUMENT],
)

TWITTER_USER_SEARCH_SUBCOMMAND = twitter_api_subcommand(
    "user-search",
    "minet.cli.twitter.user_search",
    title="Minet Twitter Users Search Command",
    description="""
        Search Twitter users using API v1.

        This will only return ~1000 results maximum per query
        so you might want to find a way to segment your inquiry
        into smaller queries to find more users.
    """,
    epilog="""
        examples:

        . Searching user using "cancer" as a query:
            $ minet tw user-search cancer > users.csv

        . Running multiple queries in series:
            $ minet tw user-search query queries.csv > users.csv
    """,
    variadic_input={"dummy_column": "query", "item_label_plural": "queries"},
    select=True,
    total=True,
)

TWITTER_USER_TWEETS_SUBCOMMAND = twitter_api_subcommand(
    "user-tweets",
    "minet.cli.twitter.user_tweets",
    title="Minet Twitter User Tweets Command",
    description="""
        Retrieve the last ~3200 tweets, including retweets from
        the given Twitter users, using the API.
    """,
    epilog="""
        examples:

        . Getting tweets from users in a CSV file:
            $ minet tw user-tweets screen_name users.csv > tweets.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "Twitter account screen name or id",
        "item_label_plural": "Twitter account screen names or ids",
    },
    select=True,
    total=True,
    arguments=[
        IDS_ARGUMENT,
        {
            "flag": "--min-date",
            "help": "Whether to add a date to stop at for user's tweets retrieval. UTC date should have the following format : YYYY-MM-DD",
            "type": TimestampType(),
        },
        {
            "flag": "--exclude-retweets",
            "help": "Whether to exclude retweets from the output.",
            "action": "store_true",
        },
        V2_ARGUMENT,
    ],
)

TWITTER_USERS_SUBCOMMAND = twitter_api_subcommand(
    "users",
    "minet.cli.twitter.users",
    title="Minet Twitter Users Command",
    description="""
        Retrieve Twitter user metadata using the API.
    """,
    epilog="""
        examples:

        . Getting friends of a list of user:
            $ minet tw users screen_name users.csv > data_users.csv
    """,
    resumer=RowCountResumer,
    select=True,
    total=True,
    variadic_input={"dummy_column": "user", "item_label": "Twitter user"},
    arguments=[
        IDS_ARGUMENT,
        V2_ARGUMENT,
    ],
)

TWITTER_COMMAND = command(
    "twitter",
    "minet.cli.twitter",
    "Minet Twitter Command",
    aliases=["tw"],
    description="""
        Gather data from Twitter.
    """,
    subcommands=[
        TWITTER_ATTRITION_SUBCOMMAND,
        TWITTER_FOLLOWERS_SUBCOMMAND,
        TWITTER_FRIENDS_SUBCOMMAND,
        TWITTER_LIST_FOLLOWERS_SUBCOMMAND,
        TWITTER_LIST_MEMBERS_SUBCOMMAND,
        TWITTER_RETWEETERS_SUBCOMMAND,
        TWITTER_SCRAPE_SUBCOMMAND,
        TWITTER_TWEET_COUNT_SUBCOMMAND,
        TWITTER_TWEET_DATE_SUBCOMMAND,
        TWITTER_TWEET_SEARCH_SUBCOMMAND,
        TWITTER_TWEETS_SUBCOMMAND,
        TWITTER_USER_SEARCH_SUBCOMMAND,
        TWITTER_USER_TWEETS_SUBCOMMAND,
        TWITTER_USERS_SUBCOMMAND,
    ],
)
