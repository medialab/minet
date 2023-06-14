from minet.cli.argparse import command

# TODO: lazyloading issue
from minet.constants import DEFAULT_THROTTLE

CRAWL_COMMAND = command(
    "crawl",
    "minet.cli.crawl.crawl",
    title="Minet Crawl Command",
    description="""
        Use multiple threads to crawl the web using minet crawling and
        scraping DSL.
    """,
    epilog="""
        Examples:

        . Running a crawler definition:
            $ minet crawl crawler.yml -O crawl-data
    """,
    no_output=True,
    arguments=[
        {"name": "crawler", "help": "Path to the crawler definition file."},
        {
            "flags": ["-O", "--output-dir"],
            "help": "Output directory.",
            "default": "crawl",
        },
        {
            "flag": "--resume",
            "help": "Whether to resume an interrupted crawl.",
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
