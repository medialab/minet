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
    InputFileAction,
    SplitterType,
    TimezoneType,
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
        validate=check_credentials,
        **kwargs
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
    selectable=True,
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
    selectable=True,
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
    selectable=True,
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
    selectable=True,
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
    selectable=True,
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
    selectable=True,
    arguments=[
        {
            "name": "items",
            "help": "What to scrape. Currently only `tweets` and `users` are possible.",
            "choices": ["tweets", "users"],
        },
        {
            "name": "query",
            "help": "Search query or name of the column containing queries to run in given CSV file.",
        },
        {
            "name": "file",
            "help": "Optional CSV file containing the queries to be run.",
            "action": InputFileAction,
            "dummy_csv_column": "query",
            "column_dest": "query",
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
    selectable=True,
    total=True,
    arguments=[
        {
            "flag": "--granularity",
            "help": "Granularity used to group the data by. Defaults to day.",
            "choices": ["minute", "hour", "day"],
        },
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
    selectable=True,
    arguments=[
        {
            "flag": "--timezone",
            "help": "Timezone for the date, for example 'Europe/Paris'. Default to UTC.",
            "type": TimezoneType(),
        }
    ],
)

TWITTER_USERS_SUBCOMMAND = twitter_api_subcommand(
    "users",
    "minet.cli.twitter.users",
    title="Minet Twitter Friends Command",
    description="""
        Retrieve friends, i.e. followed users, of given user.
    """,
    epilog="""
        examples:

        . Getting friends of a list of user:
            $ minet tw friends screen_name users.csv > friends.csv
    """,
    resumer=RowCountResumer,
    selectable=True,
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
        TWITTER_FOLLOWERS_SUBCOMMAND,
        TWITTER_FRIENDS_SUBCOMMAND,
        TWITTER_LIST_FOLLOWERS_SUBCOMMAND,
        TWITTER_LIST_MEMBERS_SUBCOMMAND,
        TWITTER_RETWEETERS_SUBCOMMAND,
        TWITTER_SCRAPE_SUBCOMMAND,
        TWITTER_TWEET_COUNT_SUBCOMMAND,
        TWITTER_TWEET_DATE_SUBCOMMAND,
        TWITTER_USERS_SUBCOMMAND,
    ],
)
