from typing import List, Optional

from urllib3 import Timeout

from minet.cli.argparse import (
    command,
    FolderStrategyType,
    BooleanAction,
    ExtractionSelectionAction,
)
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
    "resume": {
        "flag": "--resume",
        "help": "Whether to resume an interrupted crawl.",
        "action": "store_true",
    },
    "max_depth": {
        "flag": "--max-depth",
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
        "help": "Number of threads to use. Will default to a conservative number, based on the number of available cores. Feel free to increase.",
        "type": int,
    },
    "compress_on_disk": {
        "flags": ["-z", "--compress-on-disk"],
        "help": "Whether to compress the downloaded files when saving files on disk.",
        "action": "store_true",
    },
    "compress_transfer": {
        "flag": "--compress-transfer",
        "help": 'Whether to send a "Accept-Encoding" header asking for a compressed response. Usually better for bandwidth but at the cost of more CPU work.',
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
    "processes": {
        "flags": ["-p", "--processes"],
        "help": "Number of processes for the crawler process pool.",
        "type": int,
    },
    "connect_timeout": {
        "flag": "--connect-timeout",
        "help": "Maxium socket connection time to host.",
        "type": float,
        "default": 5,
    },
    "timeout": {
        "flag": "--timeout",
        "help": "Maximum time - in seconds - to spend for each request before triggering a timeout.",
        "type": float,
        "default": 30,
    },
    "retries": {
        "flag": "--retries",
        "help": "Number of times to retry on timeout & common network-related issues.",
        "type": int,
        "default": 0,
    },
    "stateful_redirects": {
        "flag": "--stateful-redirects",
        "help": "Whether to keep a cookie jar while redirecting and allowing self redirections that track state.",
        "action": "store_true",
    },
    "pycurl": {
        "flag": "--pycurl",
        "help": "Whether to use the pycurl library to perform the calls.",
        "action": "store_true",
    },
    "sqlar": {
        "flag": "--sqlar",
        "help": "Whether to write files into a single-file sqlite archive rather than as individual files on the disk.",
        "action": "store_true",
    },
}

CRAWL_MODULE_ARGUMENTS = [
    {
        "flags": ["-m", "--module"],
        "help": "Python module to import to use as spider, spiders or crawler factory. Suffix it with `:` to give actual target within module e.g. `package.module:spider`.",
    },
    {
        "flag": "--factory",
        "help": "Whether crawl target is a crawler factory function.",
        "action": "store_true",
    },
]


def crawl_command(
    name: str,
    package: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    epilog: Optional[str] = None,
    arguments: Optional[List] = None,
    accept_input: bool = True,
    accept_module: bool = False,
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
    default_retries: Optional[int] = None,
    force_spoof_user_agent: Optional[bool] = None,
    force_stateful_redirects: Optional[bool] = None,
    default_timeout: Optional[float] = None,
    default_connect_timeout: Optional[float] = None,
):
    arguments_dict = CRAWL_ARGUMENTS.copy()

    def set_default_value(k, v):
        arguments_dict[k] = {
            **arguments_dict[k],
            "default": v,
        }

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
        set_default_value("throttle", default_throttle)

    if not threads:
        del arguments_dict["threads"]

    if not domain_parallelism:
        del arguments_dict["domain_parallelism"]

    if write_files:
        del arguments_dict["write_files"]

    if not write_data:
        del arguments_dict["write_data"]
        del arguments_dict["format"]

    if default_folder_strategy is not None:
        set_default_value("folder_strategy", default_folder_strategy)

    if default_output_dir is not None:
        set_default_value("output_dir", default_output_dir)

    if default_retries is not None:
        set_default_value("retries", default_retries)

    if default_timeout is not None:
        set_default_value("timeout", default_timeout)

    if default_connect_timeout is not None:
        set_default_value("connect_timeout", default_connect_timeout)

    if force_folder_strategy is not None:
        del arguments_dict["folder_strategy"]

    if force_spoof_user_agent is not None:
        del arguments_dict["spoof_user_agent"]

    if force_stateful_redirects is not None:
        del arguments_dict["stateful_redirects"]

    arguments = (arguments or []) + list(arguments_dict.values())

    if accept_module:
        arguments.extend(CRAWL_MODULE_ARGUMENTS)

    additional_kwargs = {}

    if accept_input:
        additional_kwargs["variadic_input"] = {
            "dummy_column": "url",
            "item_label": "start url",
            "optional": True,
            "no_help": True,
        }

    epilog = (
        (epilog or "")
        + """
        Notes regarding sqlite storage temporary files:

        If you spawn a persistent crawler, some of its state will be kept using
        specialized sqlite databases on disk.

        Be aware that sqlite sometimes need to perform cleanup operations that rely
        on temporary files that will be written in a folder configured as the
        `SQLITE_TMPDIR` env variable. Be sure to set this variable when running this
        command, especially when the crawler files will be stored on a different disk
        and if writing in the host's `/tmp` directory can be risky due to insufficient
        storage available.

        For more info, check out: https://www.sqlite.org/tempfiles.html
        """
    )

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

        if not accept_module:
            cli_args.module = None
            cli_args.factory = False

        if factory:
            cli_args.factory = True

        if force_folder_strategy is not None:
            cli_args.folder_strategy = force_folder_strategy

        if force_spoof_user_agent is not None:
            cli_args.spoof_user_agent = force_spoof_user_agent

        if force_stateful_redirects is not None:
            cli_args.stateful_redirects = force_stateful_redirects

        if resolve is not None:
            resolve(cli_args)

        cli_args.timeout = Timeout(
            connect=cli_args.connect_timeout, total=cli_args.timeout
        )

        # --sqlar disables --compress-on-disk
        if cli_args.sqlar:
            cli_args.compress_on_disk = False

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

        . Using the most basic crawler following HTML links:
            $ minet crawl url -i urls.csv --max-depth 1

        . Crawling using the `process` function from the `crawl` module:
            $ minet crawl -m crawl:process -O crawl-data
    """,
    accept_module=True,
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

    if cli_args.extraction_fields and not cli_args.extract:
        raise InvalidArgumentsError(
            "Custom extraction fields can't be used if the flag extract is not present."
        )


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
            "help": "Fields of the trafilatura extraction you want to apply the content filter on, separated using commas. It must be used with the flag `--extract`.",
            "action": ExtractionSelectionAction,
            "default": None,
        },
    ],
)
