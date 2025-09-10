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
    {
        "flags": ["-l", "--lang"],
        "help": 'Bluesky Filter to posts in the given language. Expected to be based on post language field, though server may override language detection. Equivalent to "lang:<lang>" in classic search syntax.',
        "rc_key": ["bluesky", "lang"],
        "action": ConfigAction,
    },
    {
        "flag": "--since",
        "help": "Bluesky Filter results for posts after the indicated datetime (inclusive). Expected to use 'sortAt' timestamp, which is the minimum of 'createdAt' and 'indexedAt'. Can be a datetime, or just an ISO date (yyyy-mm-dd, yyyy-mm-ddThh:mm:ssZ or yyyy-mm-ddThh:mm:ss.msZ). Equivalent to \"since:<date>\" in classic search syntax.",
        "rc_key": ["bluesky", "since"],
        "action": ConfigAction,
    },
    {
        "flag": "--until",
        "help": "Bluesky Filter results for posts before the indicated datetime (NOT inclusive). Expected to use 'sortAt' timestamp, which is the minimum of 'createdAt' and 'indexedAt'. Can be a datetime, or just an ISO date (yyyy-mm-dd, yyyy-mm-ddThh:mm:ssZ or yyyy-mm-ddThh:mm:ss.msZ). Equivalent to \"until:<date>\" in classic search syntax.",
        "rc_key": ["bluesky", "until"],
        "action": ConfigAction,
    },
    {
        "flag": "--mentions",
        "help": 'Bluesky Filter to posts which mention the given account (with or without the @). Handles are resolved to DID before query-time. Only matches rich-text facet mentions. Equivalent to "mentions:<account>" in classic search syntax.',
        "rc_key": ["bluesky", "mentions"],
        "action": ConfigAction,
    },
    {
        "flag": "--author",
        "help": 'Bluesky Filter to posts by the given account (with or without the @). Handles are resolved to DID before query-time. Equivalent to "from:<account>" in classic search syntax.',
        "rc_key": ["bluesky", "author"],
        "action": ConfigAction,
    },
    {
        "flag": "--domain",
        "help": 'Bluesky Filter to posts with URLs (facet links or embeds) linking to the given domain (hostname). Server may apply hostname normalization. Equivalent to "domain:<domain>" in classic search syntax.',
        "rc_key": ["bluesky", "domain"],
        "action": ConfigAction,
    },
    {
        "flag": "--url",
        "help": "Bluesky Filter to posts with links (facet links or embeds) pointing to this URL. Server may apply URL normalization or fuzzy matching. The only equivalent in classic search syntax could be typing the URL as a keyword.",
        "rc_key": ["bluesky", "url"],
        "action": ConfigAction,
    },
    {
        "flags": ["--tag", "--hashtag"],
        "help": 'Filter to posts with the given tag (hashtag). You can include the hash (#) prefix if you wish. Multiple tags can be specified (with "AND" matching), writing them between quotes and separating them by a space. Equivalent to "#<tag>" in classic search syntax.',
        "rc_key": ["bluesky", "tag"],
        "action": ConfigAction,
    },
    {
        "flags": ["--not-keywords", "--not"],
        "help": 'Filter posts without the given keyword. Multiple keywords can be specified (with "AND" matching), writing them between quotes and separating them by a space. Equivalent to "-<keyword>" in classic search syntax.',
        "rc_key": ["bluesky", "not_keywords"],
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
