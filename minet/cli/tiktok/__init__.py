# =============================================================================
# Minet Tiktok CLI Action
# =============================================================================
#
# Logic of the `tk` action.
#
from minet.cli.argparse import command, ConfigAction
from datetime import date, timedelta

TIKTOK_HTTP_API_COMMON_ARGUMENTS = [
    {
        "flag": "--key",
        "help": "Tiktok API identification key.",
        "rc_key": ["tiktok", "api_key"],
        "action": ConfigAction,
    },
    {
        "flag": "--secret",
        "help": "Tiktok API identification secret",
        "rc_key": ["tiktok", "api_secret"],
        "action": ConfigAction,
    },
]

TIKTOK_SEARCH_VIDEOS_SUBCOMMAND = command(
    "search-videos",
    "minet.cli.tiktok.search_videos",
    title="Tiktok Search Videos Command",
    description="""
        Scrape Tiktok videos with given keyword(s).

        This requires to be logged in to an Tiktok account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        Challenges are hashtags, that can be associated with a description.

        The url have a limited life time (indicated by a timestamp in the
        url). If you want to get the resources associated to it, you should
        use the `minet fetch` command.

        This command allows you to get about 450 results, ordered by user
        relevance (a mix of most popular, and most relevant according to your
        profile).
    """,
    epilog="""
        Example:

        . Searching videos with the keyword paris:
            $ minet tiktok search-videos paris > paris_videos.csv
    """,
    variadic_input={"dummy_column": "query", "item_label": "tiktok keyword"},
    arguments=[
        {
            "flags": ["-c", "--cookie"],
            "help": 'Authenticated cookie to use or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge").',
            "default": "firefox",
            "rc_key": ["tiktok", "cookie"],
            "action": ConfigAction,
        },
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of videos to retrieve per query.",
            "type": int,
        },
    ],
)

TIKTOK_SEARCH_COMMERCIALS_SUBCOMMAND = command(
    "search-commercials",
    "minet.cli.tiktok.search_commercials",
    title="Tiktok Search Commercial Contents Command",
    description="""
        Query Tiktok commercial contents using the Ad Library API.
    """,
    epilog="""
        Example:

        . Searching all commercial contents published in Romania from October 1st to October 2nd 2024:
            $ minet tiktok search-commercials --country RO --min-date 20241001 --max-date 20241002 > romania.csv
    """,
    arguments=[
        {
            "flags": ["-c", "--country"],
            "help": "The country of the commercial content's author.",
            "type": str,
            "default": "ALL",
        },
        {
            "flags": ["--min-date"],
            "help": "Needs to be after October 1st, 2022.",
            "type": str,
            "default": "20221001",
        },
        {
            "flags": ["--max-date"],
            "help": "The end of the time range during which the commercial contents were published.",
            "type": str,
            "default": (date.today() - timedelta(days=1)).strftime("%Y%m%d"),
        },
        {
            "flags": ["-t", "--total"],
            "help": "Maximum number of contents to retrieve in total.",
            "type": int,
        },
        *TIKTOK_HTTP_API_COMMON_ARGUMENTS,
    ],
)

TIKTOK_SCRAPE_COMMERCIALS_SUBCOMMAND = command(
    "scrape-commercials",
    "minet.cli.tiktok.scrape_commercials",
    title="Tiktok Scrape Commercial Contents Command",
    description="""
        Query Tiktok commercial contents from the Ad Library website.
    """,
    epilog="""
        Example:

        . Searching all commercial contents published in Romania from October 1st to October 2nd 2024:
            $ minet tiktok scrape-commercials --country RO --min-date 20241001 --max-date 20241002 > romania.csv
    """,
    arguments=[
        {
            "flags": ["-c", "--country"],
            "help": "The country of the commercial content's author.",
            "type": str,
            "default": "all",
        },
        {
            "flags": ["--min-date"],
            "help": "Needs to be after October 1st, 2022.",
            "type": str,
            "default": "20221001",
        },
        {
            "flags": ["--max-date"],
            "help": "The end of the time range during which the commercial contents were published.",
            "type": str,
            "default": date.today().strftime("%Y%m%d"),
        },
        {
            "flags": ["-t", "--total"],
            "help": "Maximum number of contents to retrieve in total.",
            "type": int,
        },
        *TIKTOK_HTTP_API_COMMON_ARGUMENTS,
    ],
)

TIKTOK_COMMAND = command(
    "tiktok",
    "minet.cli.tiktok",
    aliases=["tk"],
    title="Minet Tiktok Command",
    description="""
        Gather data from Tiktok.
    """,
    subcommands=[
        TIKTOK_SEARCH_VIDEOS_SUBCOMMAND,
        TIKTOK_SEARCH_COMMERCIALS_SUBCOMMAND,
        TIKTOK_SCRAPE_COMMERCIALS_SUBCOMMAND,
    ],
)
