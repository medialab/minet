from minet.cli.argparse import command, ConfigAction, PartialISODatetimeType

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
    title="Minet Bluesky Firehose command",
    description="""
        Plug into the Bluesky Firehose.
    """,
)

BLUESKY_USER_FOLLOWS_COMMAND = command(
    "user-follows",
    "minet.cli.bluesky.user_follows",
    title="Minet Bluesky Get Follows from Handle or DID command",
    description="""
        Get whether follows of a user giving its handle or DID or respective follows of several users given their handle or did from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of follows to retrieve for each user. Will collect all follows by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "user"},
    epilog="""
        Examples:

        . Get follows of a user by their handle:
            $ minet bluesky user-follows @bsky.app

        . Get 100 follows of a user by their DID:
            $ minet bluesky user-follows did:plc:z72i7hdynmk6r22z27h6tvur --limit 100

        . Get follows from users by their handles from a CSV file:
            $ minet bluesky user-follows <handle-column> -i users.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky users` command.
    """,
)

BLUESKY_USER_FOLLOWERS_COMMAND = command(
    "user-followers",
    "minet.cli.bluesky.user_followers",
    title="Minet Bluesky Get Followers from Handle or DID command",
    description="""
        Get whether followers of a user giving its handle or DID or respective followers of several users given their handle or did from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of followers to retrieve for each user. Will collect all followers by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "user"},
    epilog="""
        Examples:

        . Get followers of a user by their handle:
            $ minet bluesky user-followers @bsky.app

        . Get 100 followers of a user by their DID:
            $ minet bluesky user-followers did:plc:z72i7hdynmk6r22z27h6tvur --limit 100

        . Get followers from users by their handles from a CSV file:
            $ minet bluesky user-followers <handle-column> -i users.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky users` command.
    """,
)

BLUESKY_POSTS_COMMAND = command(
    "posts",
    "minet.cli.bluesky.posts",
    title="Minet Bluesky Get Post from URI or URL command",
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
    variadic_input={"dummy_column": "post"},
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

BLUESKY_USERS_COMMAND = command(
    "users",
    "minet.cli.bluesky.users",
    title="Minet Bluesky Get User from Handle or DID command",
    description="""
        Get whether a Bluesky user given the user handle or DID or multiple Bluesky users given their handles or DIDs from column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flag": "--raw",
            "action": "store_true",
            "help": "Return the raw profile data in JSON as received from the Bluesky API instead of a normalized version.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "user"},
    epilog="""
        Examples:

        . Get user profile by their handle:
            $ minet bluesky users @bsky.app

        . Get user profile by their DID:
            $ minet bluesky users did:plc:z72i7hdynmk6r22z27h6tvur

        . Get user profiles by their handles from a CSV file:
            $ minet bluesky users <handle-column> -i users.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').
    """,
)

BLUESKY_POST_QUOTES_COMMAND = command(
    "post-quotes",
    "minet.cli.bluesky.post_quotes",
    title="Minet Bluesky Get Quotes from URL or URI command",
    description="""
        Get whether posts quoting a post giving its URL or URI or several posts quoting several posts giving their URL or URI from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of quotes to retrieve for each post. Will collect all quotes by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "post"},
    epilog="""
        Examples:

        . Get quotes for a post's URL:
            $ minet bluesky post-quotes <post-url>

        . Get 100 quotes for a post's URI:
            $ minet bluesky post-quotes <post-uri> --limit 100

        . Get quotes for posts by URLs from a CSV file:
            $ minet bluesky post-quotes <url-column> -i posts.csv

""",
)

BLUESKY_USER_POSTS_COMMAND = command(
    "user-posts",
    "minet.cli.bluesky.user_posts",
    title="Minet Bluesky Get User Posts command",
    description="""
        Retrieves Bluesky posts whether by user using its handle (e.g. @bsky.app) or DID (did:...) or multiple users given their handles or DIDs from column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    variadic_input={"dummy_column": "user"},
    arguments=[
        {
            "flags": ["-l", "--limit"],
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

BLUESKY_POST_REPOSTED_BY_COMMAND = command(
    "post-reposted-by",
    "minet.cli.bluesky.post_reposted_by",
    title="Minet Bluesky Get Reposted By from URL or URI command",
    description="""
        Get user who reposted whether a post giving its URL or URI or several posts giving their URL or URI from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of users to retrieve for each post. Will collect all users by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "post"},
    epilog="""
        Examples:

        . Get reposted by a user by a post's URL:
            $ minet bluesky post-reposted-by <post-url>

        . Get 100 reposted by user by a post's URI:
            $ minet bluesky post-reposted-by <post-uri> --limit 100

        . Get reposted by users by post URLs from a CSV file:
            $ minet bluesky post-reposted-by <url-column> -i posts.csv

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky users` command.
    """,
)

BLUESKY_RESOLVE_POST_URL_COMMAND = command(
    "resolve-post-url",
    "minet.cli.bluesky.resolve_post_url",
    title="Minet Bluesky resolve URL to URI command",
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
    title="Minet Bluesky Resolve Handle command",
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
    title="Minet Bluesky Search Post command",
    description="""
        Search for whether Bluesky posts matching a query or multiple Bluesky posts matching respectively successives queries from column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    variadic_input={"dummy_column": "query"},
    arguments=[
        {
            "flag": "--lang",
            "help": 'Filter posts in the given language. Expected to be based on post language field, though server may override language detection. Equivalent to "lang:<lang>" in classic search syntax.',
        },
        {
            "flag": "--since",
            "type": PartialISODatetimeType(True),
            "help": "Filter results for posts after the indicated datetime (inclusive). Expected to use 'createdAt' timestamp, with a millisecond precision. Can be a datetime, or just an ISO date (YYYY-MM-DD, YYYY-MM-DDTHH, ..., YYYY-MM-DDTHH:mm:SSZ or YYYY-MM-DDTHH:mm:SS.µSµSµSZ). Equivalent to \"since:<date>\" in classic search syntax.",
        },
        {
            "flag": "--until",
            "type": PartialISODatetimeType(True),
            "help": "Filter results for posts before the indicated datetime (NOT inclusive). Expected to use 'createdAt' timestamp, with a millisecond precision. Can be a datetime, or just an ISO date (YYYY-MM-DDTHH:mm:SSZ or YYYY-MM-DDTHH:mm:SS.µSµSµSZ). Equivalent to \"until:<date>\" in classic search syntax.",
        },
        {
            "flag": "--mentions",
            "help": 'Filter posts which mention the given account (with or without the @). Handles are resolved to DID before query-time. Only matches rich-text facet mentions. Equivalent to "mentions:<account>" in classic search syntax.',
        },
        {
            "flag": "--author",
            "help": 'Filter posts by the given account (with or without the @). Handles are resolved to DID before query-time. Equivalent to "from:<account>" in classic search syntax.',
        },
        {
            "flag": "--domain",
            "help": 'Filter posts with URLs (facet links or embeds) linking to the given domain (hostname). Server may apply hostname normalization. Equivalent to "domain:<domain>" in classic search syntax.',
        },
        {
            "flag": "--url",
            "help": "Filter posts with links (facet links or embeds) pointing to this URL. Server may apply URL normalization or fuzzy matching. The only equivalent in classic search syntax could be typing the URL as a keyword.",
        },
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of posts to retrieve for each query.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    epilog="""
        Examples:

        . Collect last 500 posts containing the word "new" until 2024-01-01 at 16:15 UTC:
            $ minet bsky search-posts "new" --until 2024-01-01T16:15 --limit 500 > posts.csv

        . Collect the posts containing the word "new" mentionning user "alice.bsky.social" since 2025-01-01:
            $ minet bsky search-posts "new" --mentions alice.bsky.social --since 2025-01-01 > posts.csv

        . Collect the posts containing the tag '#bluesky' in Spanish:
            $ minet bsky search-posts "#bluesky" -l es > posts.csv

        . Collect the posts containing the word "bluesky" but not the word "twitter":
            $ minet bsky search-posts "bluesky -twitter" > posts.csv

        . Collect the posts containing the word "bluesky" and a link to "youtube.com":
            $ minet bsky search-posts "bluesky" --domain youtube.com > posts.csv

        Tips:

        - You can use partial ISO dates (YYYY or YYYY-MM or YYYY-MM-DD or YYYY-MM-DDTHH or YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SS.ssssss) for the --since and --until arguments.

        - To filter posts by given tags, use the hashtag syntax, e.g. "#bluesky" in the query. Multiple tags can be specified, with 'AND' matching.

        - To filter posts without given keywords, use the minus syntax, e.g. "-twitter" in the query. Multiple keywords can be specified, with 'AND' matching.

        Warning:

        - After some tests, it seems that the posts returned by the Bluesky API are not always perfectly sorted by the local time we give (with millisecond precision). Indeed, this local time depends on the 'createdAt' field of the post, and we observed that in some cases, this value is artificial (cf their indexation code : https://github.com/bluesky-social/indigo/blob/c5eaa30f683f959af20ea17fdf390d8a22d471cd/search/transform.go#L225).
    """,
)

BLUESKY_SEARCH_USERS_COMMAND = command(
    "search-users",
    "minet.cli.bluesky.search_users",
    title="Minet Bluesky Search Users command",
    description="""
        Search for whether Bluesky users matching a query or multiple Bluesky users matching respectively successives queries from column of a CSV file. This command uses the Bluesky HTTP API. A user matches a query if the user's name, handle or bio matches the query. This command is equivalent to the classic search on Bluesky when filtering by 'People'.
    """,
    variadic_input={"dummy_column": "query"},
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of users to retrieve for each query. Will collect all users by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    epilog="""
        Examples:

        . Search user by its handle:
            $ minet bluesky search-users @bsky.app

        . Get 150 users from matching a query:
            $ minet bluesky search-users <query> --limit 150

        . Get users from a CSV file:
            $ minet bluesky search-users <query-column> -i queries.csv

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky users` command.

    """,
)

BLUESKY_COMMAND = command(
    "bluesky",
    "minet.cli.bluesky",
    aliases=["bsky"],
    title="Minet Bluesky command",
    description="""
        Collect data from Bluesky.
    """,
    subcommands=[
        BLUESKY_FIREHOSE_COMMAND,
        BLUESKY_POSTS_COMMAND,
        BLUESKY_POST_QUOTES_COMMAND,
        BLUESKY_POST_REPOSTED_BY_COMMAND,
        BLUESKY_RESOLVE_HANDLE_COMMAND,
        BLUESKY_RESOLVE_POST_URL_COMMAND,
        BLUESKY_SEARCH_POSTS_COMMAND,
        BLUESKY_SEARCH_USERS_COMMAND,
        BLUESKY_USERS_COMMAND,
        BLUESKY_USER_FOLLOWERS_COMMAND,
        BLUESKY_USER_FOLLOWS_COMMAND,
        BLUESKY_USER_POSTS_COMMAND,
    ],
)
