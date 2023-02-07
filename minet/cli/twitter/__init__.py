# =============================================================================
# Minet Twitter CLI Action
# =============================================================================
#
# Logic of the `tw` action.
#
from casanova import RowCountResumer, BatchResumer

from minet.cli.argparse import command, subcommand, ConfigAction
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
        TWITTER_USERS_SUBCOMMAND,
        TWITTER_LIST_FOLLOWERS_SUBCOMMAND,
        TWITTER_LIST_MEMBERS_SUBCOMMAND
    ],
)
