from minet.cli.argparse import command


def resolve_arguments(cli_args):
    if cli_args.column is None:
        cli_args.column = "path"


SCRAPE_COMMAND = command(
    "scrape",
    "minet.cli.scrape.scrape",
    title="Minet Scrape Command",
    description="""
        Use multiple processes to scrape data from a batch of HTML files using
        minet scraping DSL documented here:
        https://github.com/medialab/minet/blob/master/docs/cookbook/scraping_dsl.md

        It will output the scraped items as a CSV or NDJSON file.

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

        Note that a scraper can be "singular", i.e. emitting a single item per scraped
        HTML file, or "plural" if it can emit 0 or n items per file.

        Know that, for convenience, "singular" scraper will always emit a line
        per line in your input, contrary to "plural" ones. This means that sometimes
        said lines will be empty because the scraper did not match anything or if
        an error occurred.
    """,
    epilog="""
        Builtin scrapers:

        . "canonical": scrape the <link rel="canonical"> tag href if any.
        . "metas": scrape the <meta> tags if any.
        . "rss": scrape the RSS feed urls if any.
        . "title": scrape the <title> tag if any.
        . "urls": scrape all the relevant <a> tag href urls. Will join them
            with the correct base url if --url-column is valid.
        . "images": scrape all the relevant <img> tag src urls. Will join them
            with the correct base url if --url-column is valid.

        Examples:

        . Scraping a single file on disk:
            $ minet scrape scraper.yml ./path/to/file.html

        . Scraping a `minet fetch` report:
            $ minet scrape scraper.yml -i report.csv -I downloaded > scraped.csv

        . Scraping a single url:
            $ minet fetch "https://lemonde.fr" | minet scrape scraper.yml -i -

        . Indicating a custom path column (e.g. "file"):
            $ minet scrape scraper.yml file -i report.csv -I downloaded > scraped.csv

        . Scraping a CSV column containing HTML directly:
            $ minet scrape scraper.yml -i report.csv --body-column html > scraped.csv

        . Scraping a bunch of files using a glob pattern:
            $ minet scrape scraper.yml "./content/**/*.html" --glob > scraped.csv

        . Scraping using a CSV file containing glob patterns:
            $ minet scrape scraper.yml pattern -i patterns.csv --glob > scraped.csv

        . Working on a fetch report from stdin (mind the `-`):
            $ minet fetch url file.csv | minet scrape scraper.yml -i - -I downloaded > scraped.csv

        . Yielding items as newline-delimited JSON (jsonl):
            $ minet scrape scraper.yml -i report.csv --format jsonl > scraped.jsonl

        . Using a strainer to optimize performance:
            $ minet scrape links-scraper.yml --strain "a[href]" -i report.csv > links.csv

        . Keeping only some columns from input CSV file:
            $ minet scrape scraper.yml -i report.csv -s name,url > scraped.csv

        . Using a builtin scraper:
            $ minet scrape title -i report.csv > titles.csv
    """,
    resolve=resolve_arguments,
    variadic_input={"dummy_column": "path", "optional": True, "no_help": True},
    arguments=[
        {
            "name": "scraper",
            "help": 'Path to a scraper definition file, or name of a builtin scraper, e.g. "title". See the complete list below.',
        },
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
            "flag": "--url-column",
            "help": "Name of the CSV column containing the url.",
            "default": "resolved_url",
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
        {"flag": "--base-url", "help": "Base url to use if --url-column is not valid."},
        {
            "flags": ["-f", "--format"],
            "help": "Output format.",
            "choices": ["csv", "jsonl", "ndjson"],
            "default": "csv",
        },
        {
            "flag": "--plural-separator",
            "help": "Separator use to join lists of values when serializing to CSV.",
            "default": "|",
        },
        {
            "flag": "--strain",
            "help": "Optional CSS selector used to strain, i.e. only parse matched tags in the parsed html files in order to optimize performance.",
        },
        {
            "flags": ["-u", "--unordered"],
            "help": "Whether to allow the result to be written in an arbitrary order dependent on the multiprocessing scheduling. Can improve performance.",
            "action": "store_true",
        },
        {
            "flag": "--scraped-column-prefix",
            "help": "Prefix to prepend to the names of columns added by the scraper so they can be easily distinguished from columns of the input.",
        },
    ],
)
