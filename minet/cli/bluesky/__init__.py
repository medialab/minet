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

BLUESKY_FOLLOWERS_COMMAND = command(
    "followers",
    "minet.cli.bluesky.followers",
    title="Minet Bluesky Get Followers From Handle Or DID Command",
    description="""
        Get whether followers of a user giving its handle or DID or respective followers of several users given their handle or did from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flag": "--limit",
            "type": int,
            "help": "Limit the number of followers to retrieve for each user. Will collect all followers by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "handle-or-did"},
    epilog="""
        Examples:
        
        . Get followers of a user by their handle:
            $ minet bluesky followers @bsky.app

        . Get 100 followers of a user by their DID:
            $ minet bluesky followers did:plc:z72i7hdynmk6r22z27h6tvur --limit 100

        . Get followers from users by their handles from a CSV file:
            $ minet bluesky followers <handle-column> -i users.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').
    """,
)

BLUESKY_POSTS_COMMAND = command(
    "posts",
    "minet.cli.bluesky.posts",
    title="Minet Bluesky Get Post From URI or URL Command",
    description="""
        Get whether a Bluesky post given its URI or URL or multiple Bluesky posts given their URIs or URLs from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flag": "--raw",
            "action": "store_true",
            "help": "Return the raw post data in JSON as received from the Bluesky API instead of a normalized version.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "uri-or-url"},
    epilog="""
        Examples:

        . Get a post from its URI:
            $ minet bluesky posts <uri>
        
        . Get a post from its URL:
            $ minet bluesky posts <url>
        
        . Get multiple posts from their URIs from a CSV file:
            $ minet bluesky posts <uri-column> -i posts.csv

        Tips:

        - You can pass either Bluesky post URIs (at://did:...) or full URLs (https://bsky.app/profile/...) and Minet will handle the conversion for you.
    """,
)

BLUESKY_PROFILES_COMMAND = command(
    "profiles",
    "minet.cli.bluesky.profiles",
    title="Minet Bluesky Get Profile From Handle Or DID Command",
    description="""
        Get whether a Bluesky profile given the user handle or DID or multiple Bluesky profiles given their handles or DIDs from column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[*BLUESKY_HTTP_API_COMMON_ARGUMENTS],
    variadic_input={"dummy_column": "handle-or-did"},
    epilog="""
        Examples:
        
        . Get profile from a user by their handle:
            $ minet bluesky profiles @bsky.app

        . Get profile from a user by their DID:
            $ minet bluesky profiles did:plc:z72i7hdynmk6r22z27h6tvur

        . Get profiles from users by their handles from a CSV file:
            $ minet bluesky profiles <handle-column> -i users.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').
    """,
)

BLUESKY_USER_POSTS_COMMAND = command(
    "user-posts",
    "minet.cli.bluesky.user_posts",
    title="Minet Bluesky Get User Posts Command",
    description="""
        Retrieves Bluesky posts whether by user using its handle (e.g. @bsky.app) or DID (did:...) or multiple users given their handles or DIDs from column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    variadic_input={"dummy_column": "handle-or-did"},
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
            $ minet bluesky user-posts @bsky.app
        
        . Get 150 last posts from a user by their DID:
            $ minet bluesky user-posts did:plc:z72i7hdynmk6r22z27h6tvur --limit 150
        
        . Get posts from users by their handles from a CSV file:
            $ minet bluesky user-posts <handle-column> -i users.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').
    """,
)

BLUESKY_RESOLVE_POST_URL_COMMAND = command(
    "resolve-post-url",
    "minet.cli.bluesky.resolve_post_url",
    title="Minet Bluesky resolve URL to URI Command",
    description="""
        Resolve whether a Bluesky post URL to its URI or multiple Bluesky post URLs to their URIs from column of a CSV file. This command does not use the Bluesky HTTP API.
    """,
    arguments=[*BLUESKY_HTTP_API_COMMON_ARGUMENTS],
    variadic_input={"dummy_column": "url"},
    epilog="""
        Examples:
        
        . Get a post URI from its URL:
            $ minet bluesky resolve-post-url <url>

        . Get multiple post URIs from their URLs from a CSV file:
            $ minet bluesky resolve-post-url <url-column> -i posts.csv
        """,
)

BLUESKY_RESOLVE_HANDLE_COMMAND = command(
    "resolve-handle",
    "minet.cli.bluesky.resolve_handle",
    title="Minet Bluesky Resolve Handle Command",
    description="""
        Resolve whether a Bluesky handle to its DID or multiple Bluesky handles to their DIDs from column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[*BLUESKY_HTTP_API_COMMON_ARGUMENTS],
    variadic_input={"dummy_column": "handle"},
    epilog="""
        Examples:

        . Get a user DID from their handle:
            $ minet bluesky resolve-handle @bsky.app
        
        . Get multiple user DIDs from their handles from a CSV file:
            $ minet bluesky resolve-handle <handle-column> -i users.csv

        Tips:

        - You can pass the handle with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').
    """,
)

BLUESKY_SEARCH_POSTS_COMMAND = command(
    "search-posts",
    "minet.cli.bluesky.search_posts",
    title="Minet Bluesky Search Post Command",
    description="""
        Search for whether Bluesky posts matching a query or multiple Bluesky posts matching respectively successives queries from column of a CSV file. This command uses the Bluesky HTTP API.
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
        BLUESKY_FOLLOWERS_COMMAND,
        BLUESKY_POSTS_COMMAND,
        BLUESKY_PROFILES_COMMAND,
        BLUESKY_USER_POSTS_COMMAND,
        BLUESKY_RESOLVE_POST_URL_COMMAND,
        BLUESKY_RESOLVE_HANDLE_COMMAND,
        BLUESKY_SEARCH_POSTS_COMMAND,
    ],
)
