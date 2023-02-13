from minet.cli.argparse import command, InputAction
from minet.cli.constants import DEFAULT_CONTENT_FOLDER

EXTRACT_COMMAND = command(
    "extract",
    "minet.cli.extract.extract",
    title="Minet Extract Command",
    description="""
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
    epilog="""

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
    select=True,
    total=True,
    arguments=[
        {
            "name": "report",
            "help": "Input CSV fetch action report file.",
            "action": InputAction,
        },
        {
            "flags": ["-g", "--glob"],
            "help": "Whether to extract text from a bunch of html files on disk matched by a glob pattern rather than sourcing them from a CSV report.",
        },
        {
            "flags": ["-I", "--input-dir"],
            "help": 'Directory where the HTML files are stored. Defaults to "%s" if --glob is not set.'
            % DEFAULT_CONTENT_FOLDER,
        },
        {
            "flags": ["-p", "--processes"],
            "help": "Number of processes to use. Defaults to roughly half of the available CPUs.",
            "type": int,
        },
    ],
)
