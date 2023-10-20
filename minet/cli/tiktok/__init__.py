# =============================================================================
# Minet Tiktok CLI Action
# =============================================================================
#
# Logic of the `tk` action.
#
from minet.cli.argparse import command, ConfigAction

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

TIKTOK_COMMAND = command(
    "tiktok",
    "minet.cli.tiktok",
    aliases=["tk"],
    title="Minet Tiktok Command",
    description="""
        Gather data from Tiktok.
    """,
    subcommands=[TIKTOK_SEARCH_VIDEOS_SUBCOMMAND],
)
