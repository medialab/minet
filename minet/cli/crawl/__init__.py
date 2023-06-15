from minet.cli.argparse import command

# TODO: lazyloading issue
from minet.constants import DEFAULT_THROTTLE

CRAWL_COMMAND = command(
    "crawl",
    "minet.cli.crawl.crawl",
    title="Minet Crawl Command",
    description="""
        Run a crawl using a minet crawler or spiders defined
        in a python module.
    """,
    epilog="""
        Examples:

        . Crawling using the `process` function in the `crawl` module:
            $ minet crawl crawl:process -O crawl-data
    """,
    no_output=True,
    arguments=[
        {"name": "target", "help": "Crawling target."},
        {
            "flags": ["-O", "--output-dir"],
            "help": "Output directory.",
            "default": "crawl",
        },
        {"flags": ["-s", "--start-url"], "help": "Starting url."},
        {
            "flag": "--resume",
            "help": "Whether to resume an interrupted crawl.",
            "action": "store_true",
        },
        {
            "flags": ["-m", "--max-depth"],
            "help": "Maximum depth for the crawl.",
            "type": int,
        },
        {
            "flags": ["-u", "--visit-urls-only-once"],
            "help": "Whether to ensure that any url will only be visited once.",
            "action": "store_true",
        },
        {
            "flags": ["-n", "--normalized-url-cache"],
            "help": "Whether to normalize url cache when using -u/--visit-urls-only-once.",
            "action": "store_true",
        },
        {
            "flag": "--throttle",
            "help": "Time to wait - in seconds - between 2 calls to the same domain.",
            "type": float,
            "default": DEFAULT_THROTTLE,
        },
        {
            "flags": ["-f", "--format"],
            "help": "Serialization format for scraped/extracted data.",
            "choices": ("csv", "jsonl", "ndjson"),
            "default": "csv",
        },
        {
            "flags": ["-v", "--verbose"],
            "help": "Whether to print information about crawl results.",
            "action": "store_true",
        },
    ],
)
