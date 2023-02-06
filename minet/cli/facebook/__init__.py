# =============================================================================
# Minet Facebook CLI Action
# =============================================================================
#
# Logic of the `fb` action.
#
from minet.cli.argparse import command, subcommand, ConfigAction

# TODO: lazyloading issue
from minet.facebook.constants import FACEBOOK_MOBILE_DEFAULT_THROTTLE

MOBILE_ARGUMENTS = [
    {
        "flags": ["-c", "--cookie"],
        "help": 'Authenticated cookie to use or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge"). Defaults to "firefox".',
        "default": "firefox",
        "rc_key": ["facebook", "cookie"],
        "action": ConfigAction,
    },
    {
        "flag": "--throttle",
        "help": "Throttling time, in seconds, to wait between each request.",
        "type": float,
        "default": FACEBOOK_MOBILE_DEFAULT_THROTTLE,
    },
]

FACEBOOK_COMMENTS_SUBCOMMAND = subcommand(
    "comments",
    "minet.cli.facebook.comments",
    title="Minet Facebook Comments Command",
    description="""
        Scrape a Facebook post's comments.

        This requires to be logged in to a Facebook account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.
    """,
    epilog="""
        examples:

        . Scraping a post's comments:
            $ minet fb comments https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

        . Grabbing cookies from chrome:
            $ minet fb comments -c chrome https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

        . Scraping comments from multiple posts listed in a CSV file:
            $ minet fb comments post_url posts.csv > comments.csv
    """,
    variadic_input={"dummy_column": "post_url", "item_label": "post url"},
    selectable=True,
    arguments=[*MOBILE_ARGUMENTS],
)

FACEBOOK_POST_AUTHORS_SUBCOMMAND = subcommand(
    "post-authors",
    "minet.cli.facebook.post_authors",
    title="Minet Facebook Post Authors Command",
    description="""
        Retrieve the author of the given Facebook posts.

        Note that it is only relevant for group posts since
        only administrators can post something on pages.
    """,
    epilog="""
        examples:

        . Fetching authors of a series of posts in a CSV file:
            $ minet fb post-authors post_url fb-posts.csv > authors.csv
    """,
    variadic_input={"dummy_column": "post_url", "item_label": "post"},
    selectable=True,
    total=True,
    arguments=[*MOBILE_ARGUMENTS],
)

FACEBOOK_COMMAND = command(
    "facebook",
    "minet.cli.facebook",
    "Minet Facebook Command",
    aliases=["fb"],
    description="""
        Collect data from Facebook.
    """,
    subcommands=[FACEBOOK_COMMENTS_SUBCOMMAND, FACEBOOK_POST_AUTHORS_SUBCOMMAND],
)
