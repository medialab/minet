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

BLUESKY_GET_POSTS_COMMAND = command(
    "get-posts",
    "minet.cli.bluesky.get_posts",
    title="Minet Bluesky Get Post From URI or URL Command",
    description="""
        Get Bluesky post from its URI or URL.
    """,
    arguments=[*BLUESKY_HTTP_API_COMMON_ARGUMENTS],
    variadic_input={"dummy_column": "uri-or-url"},
    epilog="""
        Examples:
        
        . Get posts from their URIs:
            $ minet bluesky get-posts <uri>
        
        . Get posts from their URLs:
            $ minet bluesky get-posts <url>

        Tips:

        - You can pass either Bluesky post URIs (at://did:...) or full URLs (https://bsky.app/profile/...) and Minet will handle the conversion for you.
    """,
)

BLUESKY_GET_USER_POSTS_COMMAND = command(
    "get-user-posts",
    "minet.cli.bluesky.get_user_posts",
    title="Minet Bluesky Get User Posts Command",
    description="""
        Search for Bluesky posts by user using their handle (e.g. @bsky.app) or DID (did:...).
    """,
    variadic_input={"dummy_column": "user"},
    arguments=[
        {
            "flag": "--limit",
            "type": int,
            "help": "Limit the number of posts to retrieve for each user. Will collect all posts by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    epilog="""
        Examples:
        
        . Get posts from a user by their handle:
            $ minet bluesky get-user-posts @bsky.app
        
        . Get posts from a user by their DID:
            $ minet bluesky get-user-posts did:plc:z72i7hdynmk6r22z27h6tvur

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').
    """,
)

BLUESKY_POST_URL_TO_DID_AT_URI_COMMAND = command(
    "post-url-to-did-at-uri",
    "minet.cli.bluesky.post_url_to_did_at_uri",
    title="Minet Bluesky URL to URI Command",
    description="""
        Resolve a Bluesky post URL to its URI.
    """,
    arguments=[*BLUESKY_HTTP_API_COMMON_ARGUMENTS],
    variadic_input={"dummy_column": "url"},
)

BLUESKY_RESOLVE_HANDLE_COMMAND = command(
    "resolve-handle",
    "minet.cli.bluesky.resolve_handle",
    title="Minet Bluesky Resolve Handle Command",
    description="""
        Resolve a Bluesky handle to its DID.
    """,
    arguments=[*BLUESKY_HTTP_API_COMMON_ARGUMENTS],
    variadic_input={"dummy_column": "handle"},
    epilog="""
        Tips:

        - You can pass the handle with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').
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
    subcommands=[
        BLUESKY_FIREHOSE_COMMAND,
        BLUESKY_GET_POSTS_COMMAND,
        BLUESKY_GET_USER_POSTS_COMMAND,
        BLUESKY_POST_URL_TO_DID_AT_URI_COMMAND,
        BLUESKY_RESOLVE_HANDLE_COMMAND,
        BLUESKY_SEARCH_POSTS_COMMAND,
    ],
)
