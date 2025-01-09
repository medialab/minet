# =============================================================================
# Minet Reddit CLI Action
# =============================================================================
#
# Logic of the `rd` action.
#

from minet.cli.argparse import command

REDDIT_POSTS_SUBCOMMAND = command(
    "posts",
    "minet.cli.reddit.posts",
    title="Minet Reddit Posts Command",
    description="""
        Retrieve reddit posts from a subreddit link or name.
    """,
    epilog="""
        Example:

        . Searching posts from the subreddit r/france:
            $ minet reddit posts https://www.reddit.com/r/france > r_france_posts.csv
            $ minet reddit posts france > r_france_posts.csv
            $ minet reddit posts r/france > r_france_posts.csv
    """,
    variadic_input={
        "dummy_column": "subreddit",
        "item_label": "subreddit url, shortcode or id",
        "item_label_plural": "subreddit urls, shortcodes or ids",
    },
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of posts to retrieve.",
            "type": int,
        },
        {
            "flags": ["-t", "--text"],
            "help": "Retrieve the text of the post. Note that it will require one request per post.",
            "action": "store_true",
        },
    ],
)

REDDIT_COMMENTS_SUBCOMMAND = command(
    "comments",
    "minet.cli.reddit.comments",
    title="Minet Reddit Comments Command",
    description="""
        Retrieve comments from a reddit post link.
        Note that it will only retrieve the comments displayed on the page. If you want all the comments you need to use -A, --all but it will require a request per comment, and you can only make 100 requests per 10 minutes.
    """,
    epilog="""
        Example:

        . Searching comments from a reddit post:
            $ minet reddit comments https://www.reddit.com/r/france/comments/... > r_france_comments.csv
    """,
    variadic_input={
        "dummy_column": "post",
        "item_label": "post url, shortcode or id",
        "item_label_plural": "posts urls, shortcodes or ids",
    },
    arguments=[
        {
            "flags": ["-A", "--all"],
            "help": "Retrieve all comments.",
            "action": "store_true",
        },
    ],
)

REDDIT_USER_POSTS_SUBCOMMAND = command(
    "user-posts",
    "minet.cli.reddit.user_posts",
    title="Minet Reddit User Posts Command",
    description="""
        Retrieve reddit posts from a user link.
    """,
    epilog="""
        Example:

        . Searching posts from the user page of u/random_user:
            $ minet reddit user-posts https://www.reddit.com/user/random_user/submitted/ > random_user_posts.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "user url, shortcode or id",
        "item_label_plural": "user urls, shortcodes or ids",
    },
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of posts to retrieve.",
            "type": int,
        },
        {
            "flags": ["-t", "--text"],
            "help": "Retrieve the text of the post. Note that it will require one request per post.",
            "action": "store_true",
        },
    ],
)

REDDIT_USER_COMMENTS_SUBCOMMAND = command(
    "user-comments",
    "minet.cli.reddit.user_comments",
    title="Minet Reddit User Comments Command",
    description="""
        Retrieve reddit comments from a user link.
    """,
    epilog="""
        Example:

        . Searching comments from the user page of u/random_user:
            $ minet reddit user-comments https://www.reddit.com/user/random_user/comments/ > random_user_comments.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "user url, shortcode or id",
        "item_label_plural": "user urls, shortcodes or ids",
    },
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of comments to retrieve.",
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
        REDDIT_COMMENTS_SUBCOMMAND,
        REDDIT_USER_POSTS_SUBCOMMAND,
        REDDIT_USER_COMMENTS_SUBCOMMAND,
    ],
)
