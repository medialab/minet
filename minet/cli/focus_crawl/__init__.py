from minet.cli.argparse import command
from minet.constants import DEFAULT_THROTTLE
from minet.cli.exceptions import InvalidArgumentsError

def check_regexs(cli_args):
    rc = cli_args.regex_content
    ru = cli_args.regex_url
    if not rc and not ru:
        raise InvalidArgumentsError(
            [
                "At least one regex is required, either for URLs or content.",
                "To do so, use one of the following flags :",
                "   -r, --regex-content",
                "   -u, --regex-url"
            ]
        )

FOCUS_CRAWL_COMMAND = command(
    "focus-crawl",
    "minet.cli.focus_crawl.focus_crawl",
    resolve=check_regexs,
    title="Minet Focus Crawl Command",
    description="""
        Minet crawl feature with the possibility
        to use regular expressions to filter content.

        Regex are not case sensitive, but
        accents sensitive.

        Regex must be written between simple quotes.
    """,
    epilog="""
        Examples:

          Running a simple crawler:
            $ minet focus-crawl -i urls.csv url -r '(?:assembl[ée]e nationale|s[ée]nat)' -O ./result
    """,
    no_output=True,
    variadic_input={"dummy_column": "url"},
    arguments=[
        {
            "flags": ["-r", "--regex-content"],
            "help": "Regex used to filter fetched content.",
            "default": None,
        },
        {
            "flags": ["-u", "--regex-url"],
            "help": "Regex used to filter URLs added to crawler's queue.",
            "default": None,
        },
        {
            "flag": "--extract",
            "help": "Perform regex match on extracted text content instead of html content using the Trafilatura library.",
            "action": "store_true",
        },
        {
            "flags": ["-m", "--max-depth"],
            "help": "Max depth of the crawling exploration.",
            "default": 3,
            "type": int,
        },
        {
            "flag": "--irrelevant-continue",
            "help": "Continue exploration whether met content is relevant or not.",
            "action": "store_true",
        },
        {
            "flag": "--only-html",
            "help": "Add URLs to the crawler queue only if they seem to lead to a HTML content.",
            "action": "store_true",
        },
        {
            "flag": "--keep-irrelevant",
            "help": "Add to exported data the results judged irrelevant by the algorithm.",
            "action": "store_true",
        },
        {
            "flags": ["-O", "--output-dir"],
            "help": "Output directory.",
            "default": "focus_crawl",
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
    ],
)
