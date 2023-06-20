from minet.cli.argparse import command, FolderStrategyType

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
        --folder-strategy options:

        . "flat": default choice, all files will be written in the indicated
            content folder.

        . "fullpath": all files will be written in a folder consisting of the
            url hostname and then its path.

        . "prefix-x": e.g. "prefix-4", files will be written in folders
            having a name that is the first x characters of the file's name.
            This is an efficient way to partition content into folders containing
            roughly the same number of files if the file names are random (which
            is the case by default since md5 hashes will be used).

        . "hostname": files will be written in folders based on their url's
            full host name.

        . "normalized-hostname": files will be written in folders based on
            their url's hostname stripped of some undesirable parts (such as
            "www.", or "m." or "fr.", for instance).

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
    ],
)
