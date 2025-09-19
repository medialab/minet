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
    arguments=[
        {
            "flags": ["-l", "--lang"],
            "help": 'Filter posts in the given language. Expected to be based on post language field, though server may override language detection. Equivalent to "lang:<lang>" in classic search syntax.',
        },
        {
            "flag": "--since",
            "help": "Filter results for posts after the indicated datetime (inclusive). Expected to use 'createdAt' timestamp, with a millisecond precision. Can be a datetime, or just an ISO date (YYYY-MM-DD, YYYY-MM-DDTHH, ..., YYYY-MM-DDTHH:mm:SSZ or YYYY-MM-DDTHH:mm:SS.µSµSµSZ). Equivalent to \"since:<date>\" in classic search syntax.",
        },
        {
            "flag": "--until",
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
            "flag": "--limit",
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
