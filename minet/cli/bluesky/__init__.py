from minet.cli.argparse import command, ConfigAction

BLUESKY_HTTP_API_COMMON_ARGUMENTS = [
    {
        "flag": "--identifier",
        "help": "Bluesky personal identifier (don't forget the `.bsky.social` at the end).",
        "rc_key": ["bluesky", "identifier"],
        "action": ConfigAction,
    },
    {
        "flag": "--password",
        "help": "Bluesky app password (not your personal password, must be created here: https://bsky.app/settings/app-passwords).",
        "rc_key": ["bluesky", "password"],
        "action": ConfigAction,
    },
]

BLUESKY_FIREHOSE_COMMAND = command(
    "firehose",
    "minet.cli.bluesky.firehose",
    title="Minet Bluesky Firehose Command",
    description="""
        Plug into the Bluesky Firehose.
    """,
)

BLUESKY_SEARCH_POSTS_COMMAND = command(
    "search-posts",
    "minet.cli.bluesky.search_posts",
    title="Minet Bluesky Search Post Command",
    description="""
        Search for Bluesky posts using their HTTP API.
    """,
    variadic_input={"dummy_column": "query"},
    arguments=[*BLUESKY_HTTP_API_COMMON_ARGUMENTS],
)

BLUESKY_COMMAND = command(
    "bluesky",
    "minet.cli.bluesky",
    aliases=["bsky"],
    title="Minet Bluesky Command",
    description="""
        Collect data from Bluesky.
    """,
    subcommands=[BLUESKY_FIREHOSE_COMMAND, BLUESKY_SEARCH_POSTS_COMMAND],
)
