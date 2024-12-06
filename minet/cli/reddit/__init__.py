# =============================================================================
# Minet Reddit CLI Action
# =============================================================================
#
# Logic of the `rd` action.
#
from casanova import RowCountResumer

from minet.cli.argparse import command, ConfigAction

REDDIT_POSTS_SUBCOMMAND = command(
    "posts",
    "minet.cli.reddit.posts",
    title="Minet Reddit Posts Command",
    description="""
        Retrieve reddit posts from a subreddit link.
    """,
    epilog="""
        Example:

        . Searching posts from the subreddit r/france:
            $ minet reddit posts https://www.reddit.com/r/france > r_france_posts.csv
    """,
    variadic_input= {
        "dummy_column": "subreddit",
        "item_label": "subreddit url, subreddit shortcode or subreddit id",
        "item_label_plural": "subreddit urls, subreddit shortcodes or subreddits ids",
    },
    arguments=[
        {
            "flags": ["-n", "--number"],
            "help": "Number of posts to retrieve.",
            "type": int,
        },
    ],
)

REDDIT_COMMAND = command(
    "reddit",
    "minet.cli.reddit",
    "Minet Reddit Command",
    aliases=["rd"],
    description="""
        Collect data from Reddit.
    """,
    subcommands=[
        REDDIT_POSTS_SUBCOMMAND,
    ],
)