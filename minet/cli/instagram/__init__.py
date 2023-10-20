# =============================================================================
# Minet Instagram CLI Action
# =============================================================================
#
# Logic of the `insta` action.
#
from minet.cli.argparse import command, ConfigAction

INSTAGRAM_COMMENTS_SUBCOMMAND = command(
    "comments",
    "minet.cli.instagram.comments",
    title="Instagram Comments Command",
    description="""
        Scrape Instagram comments with a given post url, post shortcode or post id.

        This requires to be logged in to an Instagram account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.
    """,
    epilog="""
        Example:

        . Searching comments from the post https://www.instagram.com/p/CpA46rmU26Y/:
            $ minet instagram comments https://www.instagram.com/p/CpA46rmU26Y/ > comments.csv
    """,
    variadic_input={
        "dummy_column": "post",
        "item_label": "post url, post shortcode or post id",
        "item_label_plural": "post urls, post shortcodes or post ids",
    },
    select=True,
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of comments to retrieve per post.",
            "type": int,
        }
    ],
)

INSTAGRAM_HASHTAG_SUBCOMMAND = command(
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
        Example:

        . Searching posts with the hashtag paris:
            $ minet instagram hashtag paris > paris_posts.csv
    """,
    variadic_input={"dummy_column": "hashtag"},
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of posts to retrieve per hashtag.",
            "type": int,
        },
    ],
)

INSTAGRAM_USER_FOLLOWERS_SUBCOMMAND = command(
    "user-followers",
    "minet.cli.instagram.user_followers",
    title="Instagram User Followers Command",
    description="""
        Scrape Instagram followers with a given username, user url or user id.
        On verified accounts, you may be unable to get all of them.

        This requires to be logged in to an Instagram account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        Beware, instagram only provides temporary links, not permalinks,
        for profile picture urls retrieved as the "profile_pic_url" in
        the result. Be sure to download them fast if you need them (you can
        use the `minet fetch` command for that, and won't need to use cookies).

        If a username is a number without '@' at the beginning, it will be
        considered as an id.
    """,
    epilog="""
        Example:

        . Searching followers with the username banksrepeta:
            $ minet instagram user-followers banksrepeta > banksrepeta_followers.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "username, user url or user id",
        "item_label_plural": "usernames, user urls or user ids",
    },
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of followers to retrieve per user.",
            "type": int,
        },
    ],
)

INSTAGRAM_POST_INFOS_SUBCOMMAND = command(
    "post-infos",
    "minet.cli.instagram.post_infos",
    title="Instagram post-infos",
    description="""
        Scrape Instagram infos with a given post url, post shortcode or post id.

        This requires to be logged in to an Instagram account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        Beware, instagram only provides temporary links, not permalinks,
        for profile picture urls retrieved as the "profile_pic_url_hd" in
        the result. Be sure to download them fast if you need them (you can
        use the `minet fetch` command for that, and won't need to use cookies).
    """,
    epilog="""
        Example:

        . Searching infos for the post https://www.instagram.com/p/CpA46rmU26Y/:
            $ minet instagram post-infos https://www.instagram.com/p/CpA46rmU26Y/ > post_infos.csv
    """,
    variadic_input={
        "dummy_column": "post",
        "item_label": "post url, post shortcode or post id",
        "item_label_plural": "post urls, post shortcodes or post ids",
    },
    select=True,
)

INSTAGRAM_USER_FOLLOWING_SUBCOMMAND = command(
    "user-following",
    "minet.cli.instagram.user_following",
    title="Instagram User Following Command",
    description="""
        Scrape Instagram accounts followed with a given username, user url or user id.

        This requires to be logged in to an Instagram account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        Beware, instagram only provides temporary links, not permalinks,
        for profile picture urls retrieved as the "profile_pic_url" in
        the result. Be sure to download them fast if you need them (you can
        use the `minet fetch` command for that, and won't need to use cookies).

        If a username is a number without '@' at the beginning, it will be
        considered as an id.
    """,
    epilog="""
        Example:

        . Searching accounts followed with the username paramountplus:
            $ minet instagram user-following paramountplus > paramountplus_following.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "username, user url or user id",
        "item_label_plural": "usernames, user urls or user ids",
    },
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of accounts to retrieve per user.",
            "type": int,
        },
    ],
)

INSTAGRAM_USER_INFOS_SUBCOMMAND = command(
    "user-infos",
    "minet.cli.instagram.user_infos",
    title="Instagram user-infos",
    description="""
        Scrape Instagram infos with a given username, user url or user id.

        This requires to be logged in to an Instagram account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        Beware, instagram only provides temporary links, not permalinks,
        for profile picture urls retrieved as the "profile_pic_url_hd" in
        the result. Be sure to download them fast if you need them (you can
        use the `minet fetch` command for that, and won't need to use cookies).

        If a username is a number without '@' at the beginning, it will be
        considered as an id.
    """,
    epilog="""
        Example:

        . Searching infos with the username banksrepeta:
            $ minet instagram user-infos banksrepeta > banksrepeta_infos.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "username, user url or user id",
        "item_label_plural": "usernames, user urls or user ids",
    },
)

INSTAGRAM_USER_POSTS_SUBCOMMAND = command(
    "user-posts",
    "minet.cli.instagram.user_posts",
    title="Instagram User Posts Command",
    description="""
        Scrape Instagram posts with a given username, user url or user id.

        This requires to be logged in to an Instagram account, so
        by default this command will attempt to grab the relevant
        authentication cookies from a local Firefox browser.

        If you want to grab cookies from another browser or want
        to directly pass the cookie as a string, check out the
        -c/--cookie flag.

        The urls in the medias_url column have a limited life time.
        It is not the case for the url in main_thumbnail_url, which
        corresponds to the first image (the video cover if the first
        media is a video). Be sure to download them fast if you need
        them (you can use the `minet fetch` command for that, and
        won't need to use cookies).

        If a username is a number without '@' at the beginning, it will be
        considered as an id.
    """,
    epilog="""
        Example:

        . Searching posts from the account paramountplus:
            $ minet instagram user-posts paramountplus > paramountplus_posts.csv
    """,
    variadic_input={
        "dummy_column": "user",
        "item_label": "username, user url or user id",
        "item_label_plural": "usernames, user urls or user ids",
    },
    arguments=[
        {
            "flags": ["-l", "--limit"],
            "help": "Maximum number of posts to retrieve per user.",
            "type": int,
        }
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
            "help": 'Authenticated cookie to use or browser from which to extract it (supports "firefox", "chrome", "chromium", "opera" and "edge").',
            "default": "firefox",
            "rc_key": ["instagram", "cookie"],
            "action": ConfigAction,
        }
    ],
    subcommands=[
        INSTAGRAM_COMMENTS_SUBCOMMAND,
        INSTAGRAM_HASHTAG_SUBCOMMAND,
        INSTAGRAM_POST_INFOS_SUBCOMMAND,
        INSTAGRAM_USER_FOLLOWERS_SUBCOMMAND,
        INSTAGRAM_USER_FOLLOWING_SUBCOMMAND,
        INSTAGRAM_USER_INFOS_SUBCOMMAND,
        INSTAGRAM_USER_POSTS_SUBCOMMAND,
    ],
)
