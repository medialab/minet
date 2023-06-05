import codecs

from minet.cli.argparse import command
from minet.constants import DEFAULT_THROTTLE

def treat_escape(s):
    return r'{0}'.format(s)

FOCUS_CRAWL_COMMAND = command(
    "focus-crawl",
    "minet.cli.focus_crawl.focus_crawl",
    title="Minet Focus Crawl Command",
    description="""
        Minet crawl feature with the possibility
        to use regular expressions or keywords to
        filter content.

        Regex are not case sensitive, but
        accents sensitive.
    """,
    epilog="""
        Examples:

          Running a simple crawler:
            $ minet focus-crawl -i urls.csv url -r "(?:assembl[ée]e nationale|s[ée]nat)" -O ./result
    """,
    no_output=True,
    variadic_input={"dummy_column": "url"},
    arguments=[
        {
            "flags": ["-r", "--regex-content"],
            "help": "Regex used to filter fetched content.",
            #"type": treat_escape,
            "default": None
        },
        {
            "flags": ["-u", "--regex-url"],
            "help": "Regex used to filter URLs added to crawler's queue.",
            #"type": lambda s: r"{}".replace(r"\\", "\\\\").format(s),
            "default": None
        },
        {
            "flag": "--on-text",
            "help": "Perform regex match on extracted text content instead of html content.",
            "action": "store_true",
        },
        {
            "flags": ["-m", "--max-depth"],
            "help": "Max depth of the crawling exploration.",
            "default": 3
        },
        {
            "flag": "--uninteresting-continue",
            "help": "Explore whether content is interesting or not.",
            "action": "store_true"
        },
        {
            "flag": "--target-html",
            "help": "Add URLs to the crawler queue only if they seem to lead to a HTML content",
            "action": "store_true",
        },
        {
            "flag": "--keep-uninteresting",
            "help": "Add to exported data the results judged uninteresting by the algorithm",
            "action": "store_true",
        },
        {
            "flags": ["-O", "--output-dir"],
            "help": "Output directory.",
            "default": "focus_crawl"
        },
        {
            "flag": "--resume",
            "help": "Whether to resume an interrupted crawl.",
            "action": "store_true",
        },
        {
            "flag": "--dump-queue",
            "help": "Print the contents of the persistent queue. (This is for debug only, don't use this flag unless you know what you are doing).",
            "action": "store_true",
        },
        {
            "flag": "--throttle",
            "help": "Time to wait - in seconds - between 2 calls to the same domain.",
            "type": float,
            "default": DEFAULT_THROTTLE,
        },
    ]
)
