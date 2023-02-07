# =============================================================================
# Minet CLI Commands Definition
# =============================================================================
#
# Defining every minet command.
#
from argparse import FileType
from casanova import ThreadSafeResumer
from ural import is_url

from minet.constants import (
    DEFAULT_THROTTLE,
    DEFAULT_FETCH_MAX_REDIRECTS,
    DEFAULT_RESOLVE_MAX_REDIRECTS,
)
from minet.cli.constants import DEFAULT_CONTENT_FOLDER
from minet.cli.argparse import (
    BooleanAction,
    InputFileAction,
    OutputFileAction,
    SplitterType,
)

from minet.constants import COOKIE_BROWSERS

FETCH_COMMON_ARGUMENTS = [
    {
        "flag": "--domain-parallelism",
        "help": "Max number of urls per domain to hit at the same time. Defaults to 1",
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
        "flags": ["-o", "--output"],
        "action": OutputFileAction,
        "resumer": ThreadSafeResumer,
    },
    {
        "flag": "--resume",
        "help": "Whether to resume from an aborted report.",
        "action": "store_true",
    },
    {
        "flags": ["-s", "--select"],
        "help": "Columns of input CSV file to include in the output (separated by `,`).",
        "type": SplitterType(),
    },
    {
        "flags": ["--separator"],
        "help": "Character used to split the url cell in the CSV file, if this one can in fact contain multiple urls.",
    },
    {
        "flags": ["-t", "--threads"],
        "help": "Number of threads to use. Defaults to 25.",
        "type": int,
        "default": 25,
    },
    {
        "flag": "--throttle",
        "help": "Time to wait - in seconds - between 2 calls to the same domain. Defaults to %s."
        % DEFAULT_THROTTLE,
        "type": float,
        "default": DEFAULT_THROTTLE,
    },
    {
        "flag": "--timeout",
        "help": "Maximum time - in seconds - to spend for each request before triggering a timeout. Defaults to ~30s.",
        "type": float,
    },
    {
        "flag": "--total",
        "help": "Total number of lines in CSV file. Necessary if you want to display a finite progress indicator for large input files.",
        "type": int,
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

MINET_COMMANDS = {
    # Crawl action subparser
    # --------------------------------------------------------------------------
    "crawl": {
        "package": "minet.cli.crawl",
        "action": "crawl_action",
        "title": "Minet Crawl Command",
        "description": """
            Use multiple threads to crawl the web using minet crawling and
            scraping DSL.
        """,
        "epilog": """
            examples:

            . Running a crawler definition:
                $ minet crawl crawler.yml -d crawl-data
        """,
        "arguments": [
            {"name": "crawler", "help": "Path to the crawler definition file."},
            {
                "flags": ["-d", "--output-dir"],
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
                "help": "Time to wait - in seconds - between 2 calls to the same domain. Defaults to %s."
                % DEFAULT_THROTTLE,
                "type": float,
                "default": DEFAULT_THROTTLE,
            },
        ],
    },
    # Extract action subparser
    # -------------------------------------------------------------------------
    "extract": {
        "package": "minet.cli.extract",
        "action": "extract_action",
        "title": "Minet Extract Command",
        "description": """
            Use multiple processes to extract raw content and various metadata
            from a batch of HTML files. This command can either work on a
            `minet fetch` report or on a bunch of files. It will output an
            augmented report with the extracted text.

            Extraction is performed using the `trafilatura` library by Adrien
            Barbaresi. More information about the library can be found here:
            https://github.com/adbar/trafilatura

            Note that this methodology mainly targets news article and may fail
            to extract relevant content from other kind of web pages.
        """,
        "epilog": """

            columns being added to the output:

            . "extract_error": any error that happened when extracting content.
            . "canonical_url": canonical url of target html, extracted from
              link[rel=canonical].
            . "title": title of the web page, from <title> usually.
            . "description": description of the web page, as found in its
              metadata.
            . "raw_content": main content of the web page as extracted.
            . "comments": comment text whenever the heuristics succeeds in
              identifying them.
            . "author": inferred author of the web page article when found in
              its metadata.
            . "categories": list of categories extracted from the web page's
              metadata, separated by "|".
            . "tags": list of tags extracted from the web page's metadata,
              separated by "|".
            . "date": date of publication of the web page article when found in
              its metadata.
            . "sitename": canonical name as declared by the website.

            examples:

            . Extracting text from a `minet fetch` report:
                $ minet extract report.csv > extracted.csv

            . Extracting text from a bunch of files using a glob pattern:
                $ minet extract --glob "./content/**/*.html" > extracted.csv

            . Working on a report from stdin:
                $ minet fetch url_column file.csv | minet extract > extracted.csv
        """,
        "arguments": [
            {
                "name": "report",
                "help": "Input CSV fetch action report file.",
                "action": InputFileAction,
            },
            {
                "flags": ["-g", "--glob"],
                "help": "Whether to extract text from a bunch of html files on disk matched by a glob pattern rather than sourcing them from a CSV report.",
            },
            {
                "flags": ["-i", "--input-dir"],
                "help": 'Directory where the HTML files are stored. Defaults to "%s" if --glob is not set.'
                % DEFAULT_CONTENT_FOLDER,
            },
            {"flags": ["-o", "--output"], "action": OutputFileAction},
            {
                "flags": ["-p", "--processes"],
                "help": "Number of processes to use. Defaults to roughly half of the available CPUs.",
                "type": int,
            },
            {
                "flags": ["-s", "--select"],
                "help": "Columns of input CSV file to include in the output (separated by `,`).",
                "type": SplitterType(),
            },
            {
                "flag": "--total",
                "help": "Total number of HTML documents. Necessary if you want to display a finite progress indicator.",
                "type": int,
            },
        ],
    },
    # Fetch action subparser
    # --------------------------------------------------------------------------
    "fetch": {
        "package": "minet.cli.fetch",
        "action": "fetch_action",
        "title": "Minet Fetch Command",
        "description": """
            Use multiple threads to fetch batches of urls from a CSV file. The
            command outputs a CSV report with additional metadata about the
            HTTP calls and will generally write the retrieved files in a folder
            given by the user.
        """,
        "epilog": """
            columns being added to the output:

            . "index": index of the line in the original file (the output will be
              arbitrarily ordered since multiple requests are performed concurrently).
            . "resolved": final resolved url (after solving redirects) if different
              from requested url.
            . "status": HTTP status code of the request, e.g. 200, 404, 503 etc.
            . "error": an error code if anything went wrong when performing the request.
            . "filename": path to the downloaded file, relative to the folder given
              through -d/--output-dir.
            . "mimetype": detected mimetype of the requested file.
            . "encoding": detected encoding of the requested file if relevant.
            . "raw_contents": if --contents-in-report is set, will contain the
              downloaded text and the file won't be written.

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

            examples:

            . Fetching a batch of url from existing CSV file:
                $ minet fetch url_column file.csv > report.csv

            . CSV input from stdin:
                $ xsv select url_column file.csv | minet fetch url_column > report.csv

            . Fetching a single url, useful to pipe into `minet scrape`:
                $ minet fetch http://google.com | minet scrape ./scrape.json > scraped.csv
        """,
        "arguments": [
            {
                "name": "column",
                "help": "Column of the CSV file containing urls to fetch or a single url to fetch.",
            },
            {
                "name": "file",
                "help": "CSV file containing the urls to fetch.",
                "action": InputFileAction,
                "dummy_csv_column": "url",
                "dummy_csv_guard": is_url,
                "dummy_csv_error": "single argument is expected to be a valid url!",
            },
            *FETCH_COMMON_ARGUMENTS,
            {
                "flag": "--max-redirects",
                "help": "Maximum number of redirections to follow before breaking. Defaults to 5.",
                "type": int,
                "default": DEFAULT_FETCH_MAX_REDIRECTS,
            },
            {
                "flag": "--compress",
                "help": "Whether to compress the contents.",
                "action": "store_true",
            },
            {
                "flags": ["--contents-in-report", "--no-contents-in-report"],
                "help": "Whether to include retrieved contents, e.g. html, directly in the report\nand avoid writing them in a separate folder. This requires to standardize\nencoding and won't work on binary formats.",
                "dest": "contents_in_report",
                "action": BooleanAction,
            },
            {
                "flags": ["-d", "--output-dir"],
                "help": 'Directory where the fetched files will be written. Defaults to "%s".'
                % DEFAULT_CONTENT_FOLDER,
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
                "help": 'Name of the strategy to be used to dispatch the retrieved files into folders to alleviate issues on some filesystems when a folder contains too much files. Note that this will be applied on top of --filename-template. Defaults to "flat". All of the strategies are described at the end of this help.',
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
        ],
    },
    # Resolve action subparser
    # --------------------------------------------------------------------------
    "resolve": {
        "package": "minet.cli.resolve",
        "action": "resolve_action",
        "title": "Minet Resolve Command",
        "description": """
            Use multiple threads to resolve batches of urls from a CSV file. The
            command outputs a CSV report with additional metadata about the
            HTTP calls and the followed redirections.
        """,
        "epilog": """
            columns being added to the output:

            . "resolved": final resolved url (after solving redirects).
            . "status": HTTP status code of the request, e.g. 200, 404, 503 etc.
            . "error": an error code if anything went wrong when performing the request.
            . "redirects": total number of redirections to reach the final url.
            . "chain": list of redirection types separated by "|".

            examples:

            . Resolving a batch of url from existing CSV file:
                $ minet resolve url_column file.csv > report.csv

            . CSV input from stdin:
                $ xsv select url_column file.csv | minet resolve url_column > report.csv

            . Resolving a single url:
                $ minet resolve https://lemonde.fr
        """,
        "arguments": [
            {
                "name": "column",
                "help": "Column of the CSV file containing urls to resolve or a single url to resolve.",
            },
            {
                "name": "file",
                "help": "CSV file containing the urls to resolve.",
                "action": InputFileAction,
                "dummy_csv_column": "url",
            },
            *FETCH_COMMON_ARGUMENTS,
            {
                "flag": "--max-redirects",
                "help": "Maximum number of redirections to follow before breaking. Defaults to 20.",
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
    },
    # Scrape action subparser
    # -------------------------------------------------------------------------
    "scrape": {
        "package": "minet.cli.scrape",
        "action": "scrape_action",
        "title": "Minet Scrape Command",
        "description": """
            Use multiple processes to scrape data from a batch of HTML files.
            This command can either work on a `minet fetch` report or on a bunch
            of files filtered using a glob pattern.

            It will output the scraped items as a CSV file.
        """,
        "epilog": """
            examples:

            . Scraping item from a `minet fetch` report:
                $ minet scrape scraper.yml report.csv > scraped.csv

            . Working on a report from stdin:
                $ minet fetch url_column file.csv | minet scrape scraper.yml > scraped.csv

            . Scraping a single page from the web:
                $ minet fetch https://news.ycombinator.com/ | minet scrape scraper.yml > scraped.csv

            . Scraping items from a bunch of files:
                $ minet scrape scraper.yml --glob "./content/**/*.html" > scraped.csv

            . Yielding items as newline-delimited JSON (jsonl):
                $ minet scrape scraper.yml report.csv --format jsonl > scraped.jsonl

            . Only validating the scraper definition and exit:
                $ minet scraper --validate scraper.yml

            . Using a strainer to optimize performance:
                $ minet scraper links-scraper.yml --strain "a[href]" report.csv > links.csv
        """,
        "arguments": [
            {
                "name": "scraper",
                "help": "Path to a scraper definition file.",
                "type": FileType("r", encoding="utf-8"),
            },
            {
                "name": "report",
                "help": "Input CSV fetch action report file.",
                "action": InputFileAction,
            },
            {
                "flags": ["-f", "--format"],
                "help": "Output format.",
                "choices": ["csv", "jsonl"],
                "default": "csv",
            },
            {
                "flags": ["-g", "--glob"],
                "help": "Whether to scrape a bunch of html files on disk matched by a glob pattern rather than sourcing them from a CSV report.",
            },
            {
                "flags": ["-i", "--input-dir"],
                "help": 'Directory where the HTML files are stored. Defaults to "%s".'
                % DEFAULT_CONTENT_FOLDER,
            },
            {"flags": ["-o", "--output"], "action": OutputFileAction},
            {
                "flags": ["-p", "--processes"],
                "help": "Number of processes to use. Defaults to roughly half of the available CPUs.",
                "type": int,
            },
            {
                "flag": "--separator",
                "help": 'Separator use to join lists of values when output format is CSV. Defaults to "|".',
                "default": "|",
            },
            {
                "flag": "--strain",
                "help": "Optional CSS selector used to strain, i.e. only parse matched tags in the parsed html files in order to optimize performance.",
            },
            {
                "flag": "--total",
                "help": "Total number of HTML documents. Necessary if you want to display a finite progress indicator.",
                "type": int,
            },
            {
                "flag": "--validate",
                "help": "Just validate the given scraper then exit.",
                "action": "store_true",
            },
        ],
    },
    # Url Extract action subparser
    # -------------------------------------------------------------------------
    "url-extract": {
        "package": "minet.cli.url_extract",
        "action": "url_extract_action",
        "title": "Minet Url Extract Command",
        "description": """
            Extract urls from a CSV column containing either raw text or raw
            HTML.
        """,
        "epilog": """
            examples:

            . Extracting urls from a text column:
                $ minet url-extract text posts.csv > urls.csv

            . Extracting urls from a html column:
                $ minet url-extract html --from html posts.csv > urls.csv
        """,
        "arguments": [
            {"name": "column", "help": "Name of the column containing text or html."},
            {"name": "file", "help": "Target CSV file.", "action": InputFileAction},
            {"flag": "--base-url", "help": "Base url used to resolve relative urls."},
            {
                "flag": "--from",
                "help": "Extract urls from which kind of source?",
                "choices": ["text", "html"],
                "default": "text",
            },
            {"flags": ["-o", "--output"], "action": OutputFileAction},
            {
                "flags": ["-s", "--select"],
                "help": "Columns to keep in output, separated by comma.",
                "type": SplitterType(),
            },
            {
                "flag": "--total",
                "help": "Total number of lines in CSV file. Necessary if you want to display a finite progress indicator for large input files.",
                "type": int,
            },
        ],
    },
    # Url Join action subparser
    # -------------------------------------------------------------------------
    "url-join": {
        "package": "minet.cli.url_join",
        "action": "url_join_action",
        "title": "Minet Url Join Command",
        "description": """
            Join two CSV files by matching them on columns containing urls. It
            works by indexing the first file's urls in a specialized
            URL trie to match them with the second file's urls.
        """,
        "epilog": """
            examples:

            . Joining two files:
                $ minet url-join url webentities.csv post_url posts.csv > joined.csv

            . Keeping only some columns from first file:
                $ minet url-join url webentities.csv post_url posts.csv -s url,id > joined.csv
        """,
        "arguments": [
            {
                "name": "column1",
                "help": "Name of the column containing urls in the indexed file.",
            },
            {
                "name": "file1",
                "help": "Path to the file to index.",
                "action": InputFileAction,
                "nargs": None,
            },
            {
                "name": "column2",
                "help": "Name of the column containing urls in the second file.",
            },
            {
                "name": "file2",
                "help": "Path to the second file.",
                "action": InputFileAction,
                "nargs": None,
            },
            {"flags": ["-o", "--output"], "action": OutputFileAction},
            {
                "flags": ["-p", "--match-column-prefix"],
                "help": "Optional prefix to add to the first file's column names to avoid conflicts.",
                "default": "",
            },
            {
                "flags": ["-s", "--select"],
                "help": "Columns from the first file to keep, separated by comma.",
            },
            {"flag": "--separator", "help": "Split indexed url column by a separator?"},
        ],
    },
}
