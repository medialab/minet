from casanova import ThreadSafeResumer

from minet.cli.argparse import command


def resolve_arguments(cli_args):
    if cli_args.column is None:
        cli_args.column = "path"


EXTRACT_COMMAND = command(
    "extract",
    "minet.cli.extract.extract",
    title="Minet Extract Command",
    description="""
        Use multiple processes to extract the main textual content and various
        metadata item from large batches of HTML files easily and efficiently.

        Extraction of main content is performed using the `trafilatura` library
        by Adrien Barbaresi.

        Please note that this kind of main content extraction is heavily geared
        towards press articles and might not be suited to other kinds of web pages.

        More information about the library can be found here:
        https://github.com/adbar/trafilatura

        Note that this command has been geared towards working in tandem with
        the fetch command. This means the command expects, by default, CSV files
        containing columns like "path", "http_status", "encoding" etc. that
        you can find in a fetch command CSV report.

        This said, you can of course feed this command any kind of CSV data,
        and use dedicated flags such as --status-column, --body-column to
        to inform the command about your specific table.

        The command is also able to work on glob patterns, such as: "downloaded/**/*.html",
        and can also be fed CSV columns containing HTML content directly if
        required.
    """,
    epilog="""

        Columns being added to the output:

        . "extract_original_index": index of the line in the original file (the output will be
            arbitrarily ordered since multiple requests are performed concurrently).
        . "extract_error": any error that happened when extracting content.
        . "canonical_url": canonical url of target html, extracted from
            link[rel=canonical].
        . "title": title of the web page, from <title> usually.
        . "description": description of the web page, as found in its
            metadata.
        . "content": main content of the web page as extracted.
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

        Examples:

        . Extracting content from a single file on disk:
            $ minet extract ./path/to/file.html

        . Extracting content from a `minet fetch` report:
            $ minet extract -i report.csv -I downloaded > extracted.csv

        . Extracting content from a single url:
            $ minet fetch "https://lemonde.fr" | minet extract -i -

        . Indicating a custom path column (e.g. "file"):
            $ minet extract file -i report.csv -I downloaded > extracted.csv

        . Extracting content from a CSV column containing HTML directly:
            $ minet extract -i report.csv --body-column html > extracted.csv

        . Extracting content from a bunch of files using a glob pattern:
            $ minet extract "./content/**/*.html" --glob > extracted.csv

        . Extracting content using a CSV file containing glob patterns:
            $ minet extract pattern -i patterns.csv --glob > extracted.csv

        . Working on a fetch report from stdin (mind the `-`):
            $ minet fetch url file.csv | minet extract -i - -I downloaded > extracted.csv
    """,
    resolve=resolve_arguments,
    variadic_input={"dummy_column": "path", "optional": True, "no_help": True},
    resumer=ThreadSafeResumer,
    arguments=[
        {
            "flags": ["-g", "--glob"],
            "help": "Will interpret given paths as glob patterns to resolve if given.",
            "action": "store_true",
        },
        {
            "flags": ["-I", "--input-dir"],
            "help": "Directory where the HTML files are stored.",
        },
        {
            "flags": ["-p", "--processes"],
            "help": "Number of processes to use. Defaults to roughly half of the available CPUs.",
            "type": int,
        },
        {
            "flags": ["--chunk-size"],
            "help": "Chunk size for multiprocessing.",
            "type": int,
            "default": 1,
        },
        {
            "flag": "--body-column",
            "help": "Name of the CSV column containing html bodies.",
            "default": "body",
        },
        {
            "flag": "--error-column",
            "help": "Name of the CSV column containing a fetch error.",
            "default": "fetch_error",
        },
        {
            "flag": "--status-column",
            "help": "Name of the CSV column containing HTTP status.",
            "default": "http_status",
        },
        {
            "flag": "--encoding-column",
            "help": "Name of the CSV column containing file encoding.",
            "default": "encoding",
        },
        {
            "flag": "--mimetype-column",
            "help": "Name of the CSV column containing file mimetype.",
            "default": "mimetype",
        },
        {
            "flag": "--encoding",
            "help": "Name of the default encoding to use. If not given the command will infer it for you.",
        },
        {
            "flags": ["-u", "--unordered"],
            "help": "Whether to allow the result to be written in an arbitrary order dependent on the multiprocessing scheduling. Can improve performance.",
            "action": "store_true",
        },
    ],
)
