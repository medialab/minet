# =============================================================================
# Minet Twitter CLI Action
# =============================================================================
#
# Logic of the `tw` action.
#
from casanova import RowCountResumer

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
    variadic_input=("user", "CSV file containing the inquired Twitter users."),
    arguments=[
        {
            "name": "column",
            "help": "Name of the column containing the Twitter account screen names or ids.",
        },
        {
            "flag": "--ids",
            "help": "Whether your users are given as ids rather than screen names.",
            "action": "store_true",
        },
        {
            "flag": "--v2",
            "help": "Whether to use latest Twitter API v2 rather than v1.1.",
            "action": "store_true",
        },
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
    subcommands=[TWITTER_USERS_SUBCOMMAND],
)
