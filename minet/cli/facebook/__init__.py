# =============================================================================
# Minet Facebook CLI Action
# =============================================================================
#
# Logic of the `fb` action.
#
from minet.cli.argparse import command, ConfigAction

# TODO: lazyloading issue
from minet.facebook.constants import FACEBOOK_MOBILE_DEFAULT_THROTTLE

MOBILE_ARGUMENTS = [
    {
        "flags": ["-c", "--cookie"],
        "help": 'Authenticated cookie to use or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge").',
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

FACEBOOK_COMMENTS_SUBCOMMAND = command(
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
        Examples:

        . Scraping a post's comments:
            $ minet fb comments https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

        . Grabbing cookies from chrome:
            $ minet fb comments -c chrome https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

        . Scraping comments from multiple posts listed in a CSV file:
            $ minet fb comments post_url -i posts.csv > comments.csv
    """,
    variadic_input={"dummy_column": "post_url", "item_label": "post url"},
    arguments=[*MOBILE_ARGUMENTS],
)

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

FACEBOOK_POST_AUTHORS_SUBCOMMAND = command(
    "post-authors",
    "minet.cli.facebook.post_authors",
    title="Minet Facebook Post Authors Command",
    description="""
        Retrieve the author of the given Facebook posts.

        Note that it is only relevant for group posts since
        only administrators can post something on pages.
    """,
    epilog="""
        Examples:

        . Fetching authors of a series of posts in a CSV file:
            $ minet fb post-authors post_url -i fb-posts.csv > authors.csv
    """,
    variadic_input={"dummy_column": "post_url", "item_label": "post"},
    arguments=[*MOBILE_ARGUMENTS],
)

FACEBOOK_POST_STATS_SUBCOMMAND = command(
    "post-stats",
    "minet.cli.facebook.post_stats",
    title="Minet Facebook Post Stats Command",
    description="""
        Retrieve statistics about a given list of Facebook posts.
    """,
    epilog="""
        Examples:

        . Fetching stats about lists of posts in a CSV file:
            $ minet fb post-stats post_url -i fb-posts.csv > stats.csv
    """,
    variadic_input={"dummy_column": "post_url", "item_label": "post url"},
)

FACEBOOK_POST_SUBCOMMAND = command(
    "post",
    "minet.cli.facebook.post",
    title="Minet Facebook Post Command",
    description="""
        Scrape Facebook post.

        This requires to be logged in to a Facebook account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        You must set your account language to English (US) for the
        command to work.

        Note that, by default, Facebook will translate post text
        when they are not written in a language whitelisted here:
        https://www.facebook.com/settings/?tab=language

        In this case, minet will output both the original text and
        the translated one. But be aware that original text may be
        truncated, so you might want to edit your Facebook settings
        using the url above to make sure text won't be translated
        for posts you are interested in.

        Of course, the CLI will warn you when translated text is
        found so you can choose to edit your settings early as
        as possible.

        Finally, some post text is always truncated on Facebook
        when displayed in lists. This text is not yet entirely
        scraped by minet at this time.
    """,
    epilog="""
        Examples:

        . Scraping a post:
            $ minet fb post https://m.facebook.com/watch/?v=448540820705115 > post.csv

        . Grabbing cookies from chrome:
            $ minet fb posts -c chrome https://m.facebook.com/watch/?v=448540820705115 > post.csv

        . Scraping post from multiple urls listed in a CSV file:
            $ minet fb post url -i urls.csv > post.csv
    """,
    variadic_input={"dummy_column": "post_url", "item_label": "post url"},
    arguments=[*MOBILE_ARGUMENTS],
)

FACEBOOK_POSTS_SUBCOMMAND = command(
    "posts",
    "minet.cli.facebook.posts",
    title="Minet Facebook Posts Command",
    description="""
        Scrape Facebook posts.

        This requires to be logged in to a Facebook account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        Scraping posts currently only works for Facebook groups.

        Note that, by default, Facebook will translate post text
        when they are not written in a language whitelisted here:
        https://www.facebook.com/settings/?tab=language

        In this case, minet will output both the original text and
        the translated one. But be aware that original text may be
        truncated, so you might want to edit your Facebook settings
        using the url above to make sure text won't be translated
        for posts you are interested in.

        Of course, the CLI will warn you when translated text is
        found so you can choose to edit your settings early as
        as possible.

        Finally, some post text is always truncated on Facebook
        when displayed in lists. This text is not yet entirely
        scraped by minet at this time.
    """,
    epilog="""
        Examples:

        . Scraping a group's posts:
            $ minet fb posts https://www.facebook.com/groups/444175323127747 > posts.csv

        . Grabbing cookies from chrome:
            $ minet fb posts -c chrome https://www.facebook.com/groups/444175323127747 > posts.csv

        . Scraping posts from multiple groups listed in a CSV file:
            $ minet fb posts group_url -i groups.csv > posts.csv
    """,
    variadic_input={"dummy_column": "group_url", "item_label": "group url"},
    arguments=[*MOBILE_ARGUMENTS],
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
        FACEBOOK_COMMENTS_SUBCOMMAND,
        FACEBOOK_EXPERIMENTAL_COMMENTS_SUBCOMMAND,
        FACEBOOK_POST_AUTHORS_SUBCOMMAND,
        FACEBOOK_POST_STATS_SUBCOMMAND,
        FACEBOOK_POST_SUBCOMMAND,
        FACEBOOK_POSTS_SUBCOMMAND,
        FACEBOOK_URL_LIKES_SUBCOMMAND,
    ],
)
