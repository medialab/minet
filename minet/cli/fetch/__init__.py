from casanova import ThreadSafeResumer

from minet.cli.argparse import command, BooleanAction
from minet.cli.constants import DEFAULT_CONTENT_FOLDER
from minet.cli.exceptions import InvalidArgumentsError

# TODO: lazyloading issue
from minet.constants import (
    COOKIE_BROWSERS,
    DEFAULT_THROTTLE,
    DEFAULT_FETCH_MAX_REDIRECTS,
    DEFAULT_RESOLVE_MAX_REDIRECTS,
)

COMMON_ARGUMENTS = [
    {
        "flag": "--domain-parallelism",
        "help": "Max number of urls per domain to hit at the same time.",
        "type": int,
        "default": 1,
    },
    {
        "flags": ["-g", "--grab-cookies"],
        "help": 'Whether to attempt to grab cookies from your computer\'s browser (supports "firefox", "chrome", "chromium", "opera" and "edge").',
        "choices": COOKIE_BROWSERS,
    },
    {
        "flags": ["-H", "--header"],
        "help": "Custom headers used with every requests.",
        "action": "append",
        "dest": "headers",
    },
    {
        "flag": "--insecure",
        "help": "Whether to allow ssl errors when performing requests or not.",
        "action": "store_true",
    },
    {
        "flags": ["-t", "--threads"],
        "help": "Number of threads to use.",
        "type": int,
        "default": 25,
    },
    {
        "flag": "--throttle",
        "help": "Time to wait - in seconds - between 2 calls to the same domain.",
        "type": float,
        "default": DEFAULT_THROTTLE,
    },
    {
        "flag": "--timeout",
        "help": "Maximum time - in seconds - to spend for each request before triggering a timeout. Defaults to ~30s.",
        "type": float,
    },
    {
        "flag": "--url-template",
        "help": "A template for the urls to fetch. Handy e.g. if you need to build urls from ids etc.",
    },
    {
        "flags": ["-X", "--request"],
        "help": "The http method to use. Will default to GET.",
        "dest": "method",
        "default": "GET",
    },
]


def resolve_fetch_arguments(cli_args):
    # If we are hitting a single url we enable contents_in_report by default
    if cli_args.has_dummy_csv and cli_args.contents_in_report is None:
        cli_args.contents_in_report = True

    if cli_args.dont_save:
        cli_args.contents_in_report = False

    if cli_args.contents_in_report and cli_args.compress:
        raise InvalidArgumentsError(
            "Cannot both --compress and get --contents-in-report!"
        )


FETCH_COMMAND = command(
    "fetch",
    "minet.cli.fetch.fetch",
    title="Minet Fetch Command",
    description="""
        Use multiple threads to fetch batches of urls from a CSV file. The
        command outputs a CSV report with additional metadata about the
        HTTP calls and will generally write the retrieved files in a folder
        given by the user.
    """,
    epilog="""
        Columns being added to the output:

        . "fetch_original_index": index of the line in the original file (the output will be
            arbitrarily ordered since multiple requests are performed concurrently).
        . "resolved_url": final resolved url (after templating & solving redirects).
        . "http_status": HTTP status code of the request, e.g. 200, 404, 503 etc.
        . "datetime_utc": datetime when the response was finished.
        . "fetch_error": an error code if anything went wrong when performing the request.
        . "filename": path to the downloaded file, relative to the folder given
            through -O/--output-dir.
        . "mimetype": detected mimetype of the requested file.
        . "encoding": detected encoding of the requested file if relevant.
        . "body": if -c/--contents-in-report is set, will contain the
            downloaded text and the files won't be written to disk.

        --folder-strategy options:

        . "flat": default choice, all files will be written in the indicated
            content folder.

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

        . Fetching a single url (can be useful when piping):
            $ minet fetch "https://www.lemonde.fr"

        . Fetching a batch of url from existing CSV file:
            $ minet fetch url file.csv > report.csv

        . CSV input from stdin (mind the `-`):
            $ xsv select url file.csv | minet fetch url -i - > report.csv

        . Dowloading files in specific output directory:
            $ minet fetch url file.csv -O html > report.csv
    """,
    resolve=resolve_fetch_arguments,
    resumer=ThreadSafeResumer,
    variadic_input={"dummy_column": "url"},
    arguments=[
        *COMMON_ARGUMENTS,
        {
            "flag": "--max-redirects",
            "help": "Maximum number of redirections to follow before breaking.",
            "type": int,
            "default": DEFAULT_FETCH_MAX_REDIRECTS,
        },
        {
            "flag": "--compress",
            "help": "Whether to compress the contents.",
            "action": "store_true",
        },
        {
            "flags": ["-c", "--contents-in-report", "-w", "--no-contents-in-report"],
            "help": "Whether to include retrieved contents, e.g. html, directly in the report and avoid writing them in a separate folder. This requires to standardize encoding and won't work on binary formats. Note that --contents-in-report is the default when no input file is given.",
            "dest": "contents_in_report",
            "action": BooleanAction,
        },
        {
            "flags": ["-D", "--dont-save"],
            "help": "Use not to write any downloaded file on disk.",
            "action": "store_true",
        },
        {
            "flags": ["-O", "--output-dir"],
            "help": "Directory where the fetched files will be written.",
            "default": DEFAULT_CONTENT_FOLDER,
        },
        {
            "flags": ["-f", "--filename"],
            "help": 'Name of the column used to build retrieved file names. Defaults to a md5 hash of final url. If the provided file names have no extension (e.g. ".jpg", ".pdf", etc.) the correct extension will be added depending on the file type.',
        },
        {
            "flag": "--filename-template",
            "help": "A template for the name of the fetched files.",
        },
        {
            "flag": "--folder-strategy",
            "help": "Name of the strategy to be used to dispatch the retrieved files into folders to alleviate issues on some filesystems when a folder contains too much files. Note that this will be applied on top of --filename-template. All of the strategies are described at the end of this help.",
            "default": "flat",
        },
        {
            "flag": "--keep-failed-contents",
            "help": "Whether to keep & write contents for failed (i.e. non-200) http requests.",
            "action": "store_true",
        },
        {
            "flag": "--standardize-encoding",
            "help": "Whether to systematically convert retrieved text to UTF-8.",
            "action": "store_true",
        },
        {
            "flag": "--only-html",
            "help": (
                "Only download urls if they are not unambiguously not html (e.g. if the url has the .pdf or .jpg extension etc.). "
                "Then, if the url was downloaded, it will only be written on disk if the http body actually looks like html."
            ),
            "action": "store_true",
        },
    ],
)

RESOLVE_COMMAND = command(
    "resolve",
    "minet.cli.fetch.fetch",
    title="Minet Resolve Command",
    description="""
        Use multiple threads to resolve batches of urls from a CSV file. The
        command outputs a CSV report with additional metadata about the
        HTTP calls and the followed redirections.
    """,
    epilog="""
        Columns being added to the output:

        . "original_index": index of the line in the original file (the output will be
            arbitrarily ordered since multiple requests are performed concurrently).
        . "resolved_url": final resolved url (after solving redirects).
        . "http_status": HTTP status code of the request, e.g. 200, 404, 503 etc.
        . "resolution_error": an error code if anything went wrong when performing the request.
        . "redirect_count": total number of redirections to reach the final url.
        . "redirect_chain": list of redirection types separated by "|".

        Examples:

        . Resolving a batch of url from existing CSV file:
            $ minet resolve url_column file.csv > report.csv

        . CSV input from stdin (mind the `-`):
            $ xsv select url_column file.csv | minet resolve url_column - > report.csv

        . Resolving a single url:
            $ minet resolve https://lemonde.fr
    """,
    resumer=ThreadSafeResumer,
    variadic_input={"dummy_column": "url"},
    arguments=[
        *COMMON_ARGUMENTS,
        {
            "flag": "--max-redirects",
            "help": "Maximum number of redirections to follow before breaking.",
            "type": int,
            "default": DEFAULT_RESOLVE_MAX_REDIRECTS,
        },
        {
            "flag": "--follow-meta-refresh",
            "help": "Whether to follow meta refresh tags. Requires to buffer part of the response body, so it will slow things down.",
            "action": "store_true",
        },
        {
            "flag": "--follow-js-relocation",
            "help": "Whether to follow typical JavaScript window relocation. Requires to buffer part of the response body, so it will slow things down.",
            "action": "store_true",
        },
        {
            "flag": "--infer-redirection",
            "help": "Whether to try to heuristically infer redirections from the urls themselves, without requiring a HTTP call.",
            "action": "store_true",
        },
        {
            "flag": "--canonicalize",
            "help": "Whether to extract the canonical url from the html source code of the web page if found. Requires to buffer part of the response body, so it will slow things down.",
            "action": "store_true",
        },
        {
            "flag": "--only-shortened",
            "help": "Whether to only attempt to resolve urls that are probably shortened.",
            "action": "store_true",
        },
    ],
)
