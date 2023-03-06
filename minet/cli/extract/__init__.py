from minet.cli.argparse import command

EXTRACT_COMMAND = command(
    "extract",
    "minet.cli.extract.extract",
    title="Minet Extract Command",
    description="""
        Use multiple processes to extract text content and various metadata
        from a batch of HTML files.

        Extraction is performed using the `trafilatura` library by Adrien
        Barbaresi. Note that this kind of extraction was geared towards press
        articles and might not be suited to other kinds of web pages.

        More information about the library can be found here:
        https://github.com/adbar/trafilatura
    """,
    epilog="""

        columns being added to the output:

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

        examples:

        . Extracting content from a single file on disk:
            $ minet extract ./path/to/file.html

        . Extracting content from a `minet fetch` report:
            $ minet extract -i report.csv -I downloaded > extracted.csv

        . Extracting content from a single url:
            $ minet fetch "https://lemonde.fr" | minet extract

        . Extracting content from a CSV colum containing the HTML itself:
            $ minet extract -i report.csv --body-column html > extracted.csv

        . Extracting content from a bunch of files using a glob pattern:
            $ minet extract "./content/**/*.html" --glob > extracted.csv

        . Working on a report from stdin (mind the `-`):
            $ minet fetch url file.csv | minet extract filename -i - -I downloaded > extracted.csv
    """,
    variadic_input={"dummy_column": "filename", "optional": True, "no_help": True},
    arguments=[
        {
            "flags": ["-g", "--glob"],
            "help": "Will interpret given filename as glob patterns to resolve if given.",
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
            "flag": "--body-column",
            "help": "Name of the CSV column containing html bodies. Only relevant if -i/--input was given.",
            "default": "body",
        },
        {
            "flag": "--error-column",
            "help": "Name of the CSV column containing a fetch error. Only relevant if -i/--input was given.",
            "default": "fetch_error",
        },
        {
            "flag": "--status-column",
            "help": "Name of the CSV column containing HTTP status. Only relevant if -i/--input was given.",
            "default": "http_status",
        },
        {
            "flag": "--encoding-column",
            "help": "Name of the CSV column containing file encoding. Only relevant if -i/--input was given.",
            "default": "encoding",
        },
        {
            "flag": "--mimetype-column",
            "help": "Name of the CSV column containing file mimetype. Only relevant if -i/--input was given.",
            "default": "mimetype",
        },
        {
            "flag": "--encoding",
            "help": "Name of the default encoding to use. Defaults to none, i.e. the command will try to infer it for you.",
        },
    ],
)
