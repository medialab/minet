from typing import List, Optional

from minet.cli.argparse import command, FolderStrategyType
from minet.cli.exceptions import InvalidArgumentsError

# TODO: lazyloading issue
from minet.constants import DEFAULT_THROTTLE
from minet.fs import FolderStrategy

# TODO: negative int forbiding type
COMMON_CRAWL_ARGUMENTS = [
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
        "flags": ["-m", "--max-depth"],
        "help": "Maximum depth for the crawl.",
        "type": int,
    },
    {
        "flag": "--throttle",
        "help": "Time to wait - in seconds - between 2 calls to the same domain.",
        "type": float,
        "default": DEFAULT_THROTTLE,
    },
    {
        "flags": ["-t", "--threads"],
        "help": "Number of threads to use. You can use `0` if you want the crawler to remain completely synchronous.",
        "type": int,
        "default": 25,
    },
    {
        "flag": "--compress",
        "help": "Whether to compress the downloaded files when saving on disk using -w/--write.",
        "action": "store_true",
    },
    {
        "flags": ["-w", "--write"],
        "help": "Whether to write downloaded responses on disk in order to save them for later.",
        "action": "store_true",
    },
    {
        "flag": "--folder-strategy",
        "help": "Name of the strategy to be used to dispatch the retrieved files into folders to alleviate issues on some filesystems when a folder contains too much files. Note that this will be applied on top of --filename-template. All of the strategies are described at the end of this help.",
        "default": "flat",
        "type": FolderStrategyType(),
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
]

UNIQUE_CRAWL_ARGUMENTS = [
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
]

# TODO: add option to declare we will be taking a crawler or restrict some possible flags
def crawl_command(
    name: str,
    package: str,
    title: str,
    description: str,
    epilog: str = "",
    arguments: Optional[List] = None,
    accept_input: bool = True,
    resolve=None,
    unique=False,
):
    arguments = (arguments or []) + COMMON_CRAWL_ARGUMENTS

    if not unique:
        arguments.extend(UNIQUE_CRAWL_ARGUMENTS)

    additional_kwargs = {}

    if accept_input:
        additional_kwargs["variadic_input"] = {
            "dummy_column": "url",
            "item_label": "start url",
            "optional": True,
            "no_help": True,
        }

    epilog = (
        f"""
        --folder-strategy options:

        {FolderStrategy.DOCUMENTATION}

    """
        + epilog
    )

    def wrapped_resolve(cli_args):
        if unique:
            cli_args.visit_urls_only_once = True

        if resolve is not None:
            resolve(cli_args)

    return command(
        name,
        package,
        title=title,
        description=description,
        epilog=epilog,
        arguments=arguments,
        no_output=True,
        resolve=wrapped_resolve,
        **additional_kwargs,
    )


CRAWL_COMMAND = crawl_command(
    "crawl",
    "minet.cli.crawl.crawl",
    title="Minet Crawl Command",
    description="""
        Run a crawl using a minet crawler or spiders defined
        in a python module.
    """,
    epilog=f"""
        Examples:

        . Crawling using the `process` function in the `crawl` module:
            $ minet crawl crawl:process -O crawl-data
    """,
    arguments=[{"name": "target", "help": "Crawling target."}],
)


def ensure_filters(cli_args):
    if not cli_args.content_filter and not cli_args.url_filter:
        raise InvalidArgumentsError(
            [
                "At least one filter is required, either for URLs or content.",
                "To do so, use one of the following flags:",
                "   -C/--content-filter",
                "   -U/--url-filter",
            ]
        )


FOCUS_CRAWL_COMMAND = crawl_command(
    "focus-crawl",
    "minet.cli.crawl.focus_crawl",
    title="Minet Focus Crawl Command",
    description="""
        Minet crawl feature with the possibility
        to use regular expressions to filter content.

        Regex are not case sensitive, but
        accents sensitive.

        Regex must be written between simple quotes.
    """,
    epilog=f"""
        Examples:

        . Running a simple crawler:
            $ minet focus-crawl url -i urls.csv --content-filter '(?:assembl[ée]e nationale|s[ée]nat)' -O ./result
    """,
    resolve=ensure_filters,
    unique=True,
    arguments=[
        {
            "flags": ["-C", "--content-filter"],
            "help": "Regex used to filter fetched content.",
            "default": None,
        },
        {
            "flags": ["-U", "--url-filter"],
            "help": "Regex used to filter URLs added to crawler's queue.",
            "default": None,
        },
        {
            "flag": "--extract",
            "help": "Perform regex match on extracted text content instead of html content using the Trafilatura library.",
            "action": "store_true",
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
    ],
)
