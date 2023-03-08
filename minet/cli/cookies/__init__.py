# TODO: lazyloading issues
from minet.constants import COOKIE_BROWSERS

from minet.cli.argparse import command

COOKIES_COMMAND = command(
    "cookies",
    "minet.cli.cookies.cookies",
    title="Minet Cookies Command",
    description="""
        Grab cookies directly from your browsers to use them easily later
        in python scripts, for instance.
    """,
    epilog="""
        Examples:

        . Dumping cookie jar from firefox:
            $ minet cookies firefox > jar.txt

        . Dumping cookies as CSV:
            $ minet cookies firefox --csv > cookies.csv

        . Print cookie for lemonde.fr:
            $ minet cookies firefox --url https://www.lemonde.fr

        . Dump cookie morsels for lemonde.fr as CSV:
            $ minet cookies firefox --url https://www.lemonde.fr --csv > morsels.csv
    """,
    arguments=[
        {
            "name": "browser",
            "help": "Name of the browser from which to grab cookies.",
            "choices": COOKIE_BROWSERS,
        },
        {
            "flag": "--csv",
            "help": "Whether to format the output as CSV. If --url is set, will output the cookie's morsels as CSV.",
            "action": "store_true",
        },
        {
            "flag": "--url",
            "help": "If given, only returns full cookie header value for this url.",
        },
    ],
)
