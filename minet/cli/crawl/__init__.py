from typing import List, Optional

from minet.cli.argparse import command, FolderStrategyType, BooleanAction, InputAction
from minet.cli.exceptions import InvalidArgumentsError

# TODO: lazyloading issue
from minet.constants import DEFAULT_THROTTLE
from minet.fs import FolderStrategy

# TODO: negative int forbiding type
CRAWL_ARGUMENTS = {
    "output_dir": {
        "flags": ["-O", "--output-dir"],
        "help": "Output directory.",
        "default": "crawl",
    },
    "factory": {
        "flag": "--factory",
        "help": "Whether crawl target is a crawler factory function.",
        "action": "store_true",
    },
    "resume": {
        "flag": "--resume",
        "help": "Whether to resume an interrupted crawl.",
        "action": "store_true",
    },
    "max_depth": {
        "flags": ["-m", "--max-depth"],
        "help": "Maximum depth for the crawl.",
        "type": int,
    },
    "throttle": {
        "flag": "--throttle",
        "help": "Time to wait - in seconds - between 2 calls to the same domain.",
        "type": float,
        "default": DEFAULT_THROTTLE,
    },
    "domain_parallelism": {
        "flag": "--domain-parallelism",
        "help": "Max number of urls per domain to hit at the same time.",
        "type": int,
        "default": 1,
    },
    "threads": {
        "flags": ["-t", "--threads"],
        "help": "Number of threads to use. You can use `0` if you want the crawler to remain completely synchronous.",
        "type": int,
        "default": 25,
    },
    "compress": {
        "flags": ["-z", "--compress"],
        "help": "Whether to compress the downloaded files when saving files on disk.",
        "action": "store_true",
    },
    "write_files": {
        "flags": ["-w", "--write-files"],
        "help": "Whether to write downloaded files on disk in order to save them for later.",
        "action": "store_true",
    },
    "write_data": {
        "flags": ["-d", "--write-data", "-D", "--dont-write-data"],
        "help": "Whether to write scraped/extracted data on disk.",
        "action": BooleanAction,
        "default": True,
    },
    "folder_strategy": {
        "flag": "--folder-strategy",
        "help": "Name of the strategy to be used to dispatch the retrieved files into folders to alleviate issues on some filesystems when a folder contains too much files. Note that this will be applied on top of --filename-template. All of the strategies are described at the end of this help.",
        "default": "flat",
        "type": FolderStrategyType(),
    },
    "format": {
        "flags": ["-f", "--format"],
        "help": "Serialization format for scraped/extracted data.",
        "choices": ("csv", "jsonl", "ndjson"),
        "default": "csv",
    },
    "verbose": {
        "flags": ["-v", "--verbose"],
        "help": "Whether to print information about crawl results.",
        "action": "store_true",
    },
    "visit_urls_only_once": {
        "flags": ["-u", "--visit-urls-only-once"],
        "help": "Whether to ensure that any url will only be visited once.",
        "action": "store_true",
    },
    "normalized_url_cache": {
        "flags": ["-n", "--normalized-url-cache"],
        "help": "Whether to normalize url cache used to assess if some url was already visited.",
        "action": "store_true",
    },
    "insecure": {
        "flags": ["-k", "--insecure"],
        "help": "Whether to allow ssl errors when performing requests or not.",
        "action": "store_true",
    },
    "spoof_user_agent": {
        "flag": "--spoof-user-agent",
        "help": 'Whether to use a plausible random "User-Agent" header when making requests.',
        "action": "store_true",
    },
}


def crawl_command(
    name: str,
    package: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    epilog: Optional[str] = None,
    arguments: Optional[List] = None,
    accept_input: bool = True,
    resolve=None,
    unique: bool = False,
    url_cache: bool = True,
    max_depth: bool = True,
    throttle: bool = True,
    default_throttle: Optional[float] = None,
    domain_parallelism: bool = True,
    threads: bool = True,
    write_files: bool = False,
    write_data: bool = True,
    factory: bool = False,
    default_folder_strategy: Optional[str] = None,
    force_folder_strategy: Optional[str] = None,
    default_output_dir: Optional[str] = None,
):
    arguments_dict = CRAWL_ARGUMENTS.copy()

    # NOTE: missing a lot in the resolve here
    if unique:
        del arguments_dict["visit_urls_only_once"]

    if not url_cache:
        del arguments_dict["visit_urls_only_once"]
        del arguments_dict["normalized_url_cache"]

    if not max_depth:
        del arguments_dict["max_depth"]

    if not throttle:
        del arguments_dict["throttle"]

    if default_throttle is not None:
        arguments_dict["throttle"] = {
            **arguments_dict["throttle"],
            "default": default_throttle,
        }

    if not threads:
        del arguments_dict["threads"]

    if not domain_parallelism:
        del arguments_dict["domain_parallelism"]

    if write_files:
        del arguments_dict["write_files"]

    if not write_data:
        del arguments_dict["write_data"]
        del arguments_dict["format"]

    if factory:
        del arguments_dict["factory"]

    if default_folder_strategy is not None:
        arguments_dict["folder_strategy"] = {
            **arguments_dict["folder_strategy"],
            "default": default_folder_strategy,
        }

    if default_output_dir is not None:
        arguments_dict["output_dir"] = {
            **arguments_dict["output_dir"],
            "default": default_output_dir,
        }

    if force_folder_strategy is not None:
        del arguments_dict["folder_strategy"]

    arguments = (arguments or []) + list(arguments_dict.values())

    additional_kwargs = {}

    if accept_input:
        additional_kwargs["variadic_input"] = {
            "dummy_column": "url",
            "item_label": "start url",
            "optional": True,
            "no_help": True,
        }

    if "folder_strategy" in arguments_dict:
        # NOTE: text indentation IS important
        epilog = f"""
        --folder-strategy options:

        {FolderStrategy.DOCUMENTATION}

        """ + (
            epilog or ""
        )

    def wrapped_resolve(cli_args):
        if unique:
            cli_args.visit_urls_only_once = True

        if write_files:
            cli_args.write_files = True

        if not write_data:
            cli_args.write_data = False

        if factory:
            cli_args.factory = True

        if force_folder_strategy is not None:
            cli_args.folder_strategy = force_folder_strategy

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


def check_focus_crawl_arguments(cli_args):
    if not cli_args.content_filter and not cli_args.url_filter:
        raise InvalidArgumentsError(
            [
                "At least one filter is required, either for URLs or content.",
                "To do so, use one of the following flags:",
                "   -C/--content-filter",
                "   -U/--url-filter",
            ]
        )

    TRAFILATURA_FIELDS = [
        "title",
        "description",
        "content",
        "comments",
        "author",
        "categories",
        "tags",
        "date",
        "sitename",
    ]

    fields = set(cli_args.extraction_fields.split(","))

    for field in fields:
        if not field in TRAFILATURA_FIELDS:
            raise InvalidArgumentsError(
                [
                    f"The trafilatura field `{field}` doesn't exist. Available fields are :"
                ]
                + [f"- {a}" for a in TRAFILATURA_FIELDS]
            )

    cli_args.extraction_fields = fields


FOCUS_CRAWL_COMMAND = crawl_command(
    "focus-crawl",
    "minet.cli.crawl.focus",
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

        . Running a simple crawler:
            $ minet focus-crawl url -i urls.csv --content-filter '(?:assembl[ée]e nationale|s[ée]nat)' -O ./result
    """,
    resolve=check_focus_crawl_arguments,
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
            "flag": "--invert-content-match",
            "help": "Flag to turn the content filter into an exclusion rule.",
            "action": "store_true",
        },
        {
            "flag": "--invert-url-match",
            "help": "Flag to turn the url filter into an exclusion rule.",
            "action": "store_true",
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
            "flag": "--extraction-fields",
            "help": "Fields of the trafilatura extraction you want to apply the content filter on, separated using commas. It enables the flag `--extract`. Available flags are : `title`, `description`, `content`, `comments`, `author`, `categories`, `tags`, `date` and `sitename`.",
            "default": None,
        },
    ],
)

HYPHE_CRAWL_COMMAND = crawl_command(
    "hyphe-crawl",
    "minet.cli.crawl.hyphe",
    title="Minet Hyphe Crawl Command",
    description="""
        Specialized crawl command that can be used to reproduce
        a Hyphe crawl from a corpus exported in CSV.
    """,
    epilog="""
        Examples:

        . Reproducing a crawl:
            $ minet hyphe-crawl corpus.csv
    """,
    unique=True,
    accept_input=False,
    default_folder_strategy="fullpath",
    default_throttle=0,
    arguments=[
        {
            "name": "corpus",
            "action": InputAction,
            "help": "Path to the Hyphe corpus exported to CSV.",
        },
        {
            "flag": "--id-column",
            "default": "ID",
            "help": "Name of the CSV column containing the webentity ids.",
        },
        {
            "flag": "--status-column",
            "default": "STATUS",
            "help": "Name of the CSV column containing the webentity statuses.",
        },
        {
            "flag": "--prefixes-column",
            "default": "PREFIXES AS URL",
            "help": "Name of the CSV column containing the webentity prefixes, separated by --prefix-separator.",
        },
        {
            "flag": "--prefix-separator",
            "default": " ",
            "help": "Separator character for the webentity prefixes.",
        },
        {
            "flag": "--start-pages-column",
            "default": "START PAGES",
            "help": "Name of the CSV column containing the webentity start pages, separated by --start-page-separator.",
        },
        {
            "flag": "--start-page-separator",
            "default": " ",
            "help": "Separator character for the webentity start pages.",
        },
    ],
)
