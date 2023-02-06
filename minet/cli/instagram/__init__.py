# =============================================================================
# Minet Instagram CLI Action
# =============================================================================
#
# Logic of the `insta` action.
#
from minet.cli.argparse import command, subcommand, ConfigAction

INSTAGRAM_HASHTAG_SUBCOMMAND = subcommand(
    "hashtag",
    "minet.cli.instagram.hashtag",
    title="Instagram hashtag",
    description="""
        Scrape Instagram posts with a given hashtag.

        This requires to be logged in to an Instagram account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        display_url is not the media url, but a thumbnail of the post.
        There is no way with this command to get the media urls.
    """,
    epilog="""
        example:

        . Searching posts with the hashtag paris:
            $ minet instagram hashtag paris > paris_posts.csv
    """,
    variadic_input={"dummy_column": "hashtag"},
    selectable=True,
    total=True,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of posts to retrieve per hashtag.",
            "type": int,
        },
    ],
)

INSTAGRAM_COMMAND = command(
    "instagram",
    "minet.cli.instagram",
    aliases=["insta"],
    title="Minet Instagram Command",
    description="""
        Gather data from Instagram.
    """,
    common_arguments=[
        {
            "flags": ["-c", "--cookie"],
            "help": 'Authenticated cookie to use or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge"). Defaults to "firefox".',
            "default": "firefox",
            "rc_key": ["instagram", "cookie"],
            "action": ConfigAction,
        }
    ],
    subcommands=[INSTAGRAM_HASHTAG_SUBCOMMAND],
)
