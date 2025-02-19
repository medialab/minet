# =============================================================================
# Minet Facebook CLI Action
# =============================================================================
#
# Logic of the `fb` action.
#
from minet.cli.argparse import command

FACEBOOK_EXPERIMENTAL_COMMENTS_SUBCOMMAND = command(
    "experimental-comments",
    "minet.cli.facebook.experimental_comments",
    title="Minet Experimental Facebook Comments Command",
    description="""
        Scrape a Facebook post's comments using an experimental scraper
        based on browser emulation.
    """,
    epilog="""
        Examples:

        . Scraping a post's comments:
            $ minet fb experimental-comments https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

        . Scraping comments from multiple posts listed in a CSV file:s
            $ minet fb experimental-comments post_url -i posts.csv > comments.csv
    """,
    variadic_input={"dummy_column": "post_url", "item_label": "post url"},
    arguments=[
        {
            "flag": "--headful",
            "help": "Whether to disable the browser's headless mode for debugging purposes.",
            "action": "store_true",
        }
    ],
)

FACEBOOK_URL_LIKES_SUBCOMMAND = command(
    "url-likes",
    "minet.cli.facebook.url_likes",
    title="Minet Facebook Url Likes Command",
    description="""
        Retrieve the approximate number of "likes" (actually an aggregated engagement metric)
        that a url got on Facebook. The command can also be used with a list of urls stored in a CSV file.
        This number is found by scraping Facebook's share button, which only gives a
        rough estimation of the real engagement metric: "Share 45K" for example.

        Note that this number does not actually only correspond to the number of
        likes or shares, but it is rather the sum of like, love, ahah, angry, etc.
        reactions plus the number of comments and shares that the URL got on Facebook
        (here is the official documentation: https://developers.facebook.com/docs/plugins/faqs
        explaining "What makes up the number shown next to my Share button?").
    """,
    epilog="""
        example:
        . Retrieving the "like" number for one url:
            $ minet fb url-likes "www.example-url.com" > url_like.csv

        . Retrieving the "like" number for the urls listed in a CSV file:
            $ minet fb url-likes url -i url.csv > url_likes.csv
    """,
    variadic_input={"dummy_column": "url", "item_label": "url"},
)

FACEBOOK_COMMAND = command(
    "facebook",
    "minet.cli.facebook",
    "Minet Facebook Command",
    aliases=["fb"],
    description="""
        Collect data from Facebook.
    """,
    subcommands=[
        FACEBOOK_EXPERIMENTAL_COMMENTS_SUBCOMMAND,
        FACEBOOK_URL_LIKES_SUBCOMMAND,
    ],
)
