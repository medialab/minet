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
    arguments=[
        {
            "flag": "--since",
            "type": PartialISODatetimeType(False),
            "help": "Start collecting posts from the given datetime (inclusive, timezone UTC). Note that the Bluesky Jetstream firehose only allows to start from up to one day in the past. Moreover, note that the date used correspons to the firehose event timestamp, only used for configuring or debugging the firehose itself, so it might not corresponds exactly to the first collected post dates.",
        }
    ]
)

BLUESKY_PROFILE_FOLLOWS_COMMAND = command(
    "profile-follows",
    "minet.cli.bluesky.profile_follows",
    title="Minet Bluesky Get Follows from Handle or DID command",
    description="""
        Get whether follows of a profile giving its handle or DID or respective follows of several profiles given their handle or did from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of follows to retrieve for each profile. Will collect all follows by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "profile"},
    epilog="""
        Examples:

        . Get follows of a profile by their handle:
            $ minet bluesky profile-follows @bsky.app

        . Get 100 follows of a profile by their DID:
            $ minet bluesky profile-follows did:plc:z72i7hdynmk6r22z27h6tvur --limit 100

        . Get follows from profiles by their handles from a CSV file:
            $ minet bluesky profile-follows <handle-column> -i profiles.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.
    """,
)

BLUESKY_PROFILE_FOLLOWERS_COMMAND = command(
    "profile-followers",
    "minet.cli.bluesky.profile_followers",
    title="Minet Bluesky Get Followers from Handle or DID command",
    description="""
        Get whether followers of a profile giving its handle or DID or respective followers of several profiles given their handle or did from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of followers to retrieve for each profile. Will collect all followers by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "profile"},
    epilog="""
        Examples:

        . Get followers of a profile by their handle:
            $ minet bluesky profile-followers @bsky.app

        . Get 100 followers of a profile by their DID:
            $ minet bluesky profile-followers did:plc:z72i7hdynmk6r22z27h6tvur --limit 100

        . Get followers from profiles by their handles from a CSV file:
            $ minet bluesky profile-followers <handle-column> -i profiles.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.
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

BLUESKY_PROFILES_COMMAND = command(
    "profiles",
    "minet.cli.bluesky.profiles",
    title="Minet Bluesky Get Profile from Handle or DID command",
    description="""
        Get whether a Bluesky profile given the profile handle or DID or multiple Bluesky profiles given their handles or DIDs from column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flag": "--raw",
            "action": "store_true",
            "help": "Return the raw profile data in JSON as received from the Bluesky API instead of a normalized version.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "profile"},
    epilog="""
        Examples:

        . Get profile by their handle:
            $ minet bluesky profiles @bsky.app

        . Get profile by their DID:
            $ minet bluesky profiles did:plc:z72i7hdynmk6r22z27h6tvur

        . Get profiles by their handles from a CSV file:
            $ minet bluesky profiles <handle-column> -i profiles.csv

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

BLUESKY_PROFILE_POSTS_COMMAND = command(
    "profile-posts",
    "minet.cli.bluesky.profile_posts",
    title="Minet Bluesky Get Profile Posts command",
    description="""
        Retrieves Bluesky posts whether by profile using its handle (e.g. @bsky.app) or DID (did:...) or multiple profiles given their handles or DIDs from column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    variadic_input={"dummy_column": "profile"},
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of posts to retrieve for each profile. Will collect all posts by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    epilog="""
        Examples:

        . Get posts from a profile by their handle:
            $ minet bluesky profile-posts @bsky.app

        . Get 150 last posts from a profile by their DID:
            $ minet bluesky profile-posts did:plc:z72i7hdynmk6r22z27h6tvur --limit 150

        . Get posts from profiles by their handles from a CSV file:
            $ minet bluesky profile-posts <handle-column> -i profiles.csv

        Tips:

        - If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').
    """,
)

BLUESKY_POST_LIKED_BY_COMMAND = command(
    "post-liked-by",
    "minet.cli.bluesky.post_liked_by",
    title="Minet Bluesky Get Liked By from URL or URI command",
    description="""
        Get profile who liked whether a post giving its URL or URI or several posts giving their URL or URI from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of profiles to retrieve for each post. Will collect all profiles by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "post"},
    epilog="""
        Examples:

        . Get profiles who liked a post from the post's URL:
            $ minet bluesky post-liked-by <post-url>

        . Get 100 profiles who liked a post from the post's URI:
            $ minet bluesky post-liked-by <post-uri> --limit 100

        . Get profiles who liked a post from post URLs from a CSV file:
            $ minet bluesky post-liked-by <url-column> -i posts.csv

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.
    """,
)

BLUESKY_POST_REPOSTED_BY_COMMAND = command(
    "post-reposted-by",
    "minet.cli.bluesky.post_reposted_by",
    title="Minet Bluesky Get Reposted By from URL or URI command",
    description="""
        Get profile who reposted whether a post giving its URL or URI or several posts giving their URL or URI from the column of a CSV file. This command uses the Bluesky HTTP API.
    """,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of profiles to retrieve for each post. Will collect all profiles by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    variadic_input={"dummy_column": "post"},
    epilog="""
        Examples:

        . Get profiles who reposted a post from the post's URL:
            $ minet bluesky post-reposted-by <post-url>

        . Get 100 profiles who reposted a post from the post's URI:
            $ minet bluesky post-reposted-by <post-uri> --limit 100

        . Get profiles who reposted a post from post URLs from a CSV file:
            $ minet bluesky post-reposted-by <url-column> -i posts.csv

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.
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

        . Get a profile DID from their handle:
            $ minet bluesky resolve-handle @bsky.app

        . Get multiple profile DIDs from their handles from a CSV file:
            $ minet bluesky resolve-handle <handle-column> -i profiles.csv

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

        . Collect the posts containing the word "new" mentionning profile "alice.bsky.social" since 2025-01-01:
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

BLUESKY_SEARCH_PROFILES_COMMAND = command(
    "search-profiles",
    "minet.cli.bluesky.search_profiles",
    title="Minet Bluesky Search Profiles command",
    description="""
        Search for whether Bluesky profiles matching a query or multiple Bluesky profiles matching respectively successives queries from column of a CSV file. This command uses the Bluesky HTTP API. A profile matches a query if the profile's name, handle or bio matches the query. This command is equivalent to the classic search on Bluesky when filtering by 'People'.
    """,
    variadic_input={"dummy_column": "query"},
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "type": int,
            "help": "Limit the number of profiles to retrieve for each query. Will collect all profiles by default.",
        },
        *BLUESKY_HTTP_API_COMMON_ARGUMENTS,
    ],
    epilog="""
        Examples:

        . Search profile by its handle:
            $ minet bluesky search-profiles @bsky.app

        . Get 150 profiles from matching a query:
            $ minet bluesky search-profiles <query> --limit 150

        . Get profiles from a CSV file:
            $ minet bluesky search-profiles <query-column> -i queries.csv

        Note:

        - This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.

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
        BLUESKY_POST_LIKED_BY_COMMAND,
        BLUESKY_POST_QUOTES_COMMAND,
        BLUESKY_POST_REPOSTED_BY_COMMAND,
        BLUESKY_RESOLVE_HANDLE_COMMAND,
        BLUESKY_RESOLVE_POST_URL_COMMAND,
        BLUESKY_SEARCH_POSTS_COMMAND,
        BLUESKY_SEARCH_PROFILES_COMMAND,
        BLUESKY_PROFILES_COMMAND,
        BLUESKY_PROFILE_FOLLOWERS_COMMAND,
        BLUESKY_PROFILE_FOLLOWS_COMMAND,
        BLUESKY_PROFILE_POSTS_COMMAND,
    ],
)
