from argparse import FileType

from minet.cli.argparse import command, InputAction
from minet.cli.constants import DEFAULT_CONTENT_FOLDER

SCRAPE_COMMAND = command(
    "scrape",
    "minet.cli.scrape.scrape",
    title="Minet Scrape Command",
    description="""
        Use multiple processes to scrape data from a batch of HTML files.
        This command can either work on a `minet fetch` report or on a bunch
        of files filtered using a glob pattern.

        It will output the scraped items as a CSV file.
    """,
    epilog="""
        examples:

        . Scraping item from a `minet fetch` report:
            $ minet scrape scraper.yml report.csv > scraped.csv

        . Working on a report from stdin (mind the `-`):
            $ minet fetch url_column file.csv | minet scrape scraper.yml - > scraped.csv

        . Scraping a single page from the web:
            $ minet fetch https://news.ycombinator.com/ | minet scrape scraper.yml - > scraped.csv

        . Scraping items from a bunch of files:
            $ minet scrape scraper.yml --glob "./content/**/*.html" > scraped.csv

        . Yielding items as newline-delimited JSON (jsonl):
            $ minet scrape scraper.yml report.csv --format jsonl > scraped.jsonl

        . Only validating the scraper definition and exit:
            $ minet scraper --validate scraper.yml

        . Using a strainer to optimize performance:
            $ minet scraper links-scraper.yml --strain "a[href]" report.csv > links.csv
    """,
    total=True,
    arguments=[
        {
            "name": "scraper",
            "help": "Path to a scraper definition file.",
            "type": FileType("r", encoding="utf-8"),
        },
        {
            "name": "report",
            "help": "Input CSV fetch action report file.",
            "action": InputAction,
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
            "flags": ["-I", "--input-dir"],
            "help": 'Directory where the HTML files are stored. Defaults to "%s".'
            % DEFAULT_CONTENT_FOLDER,
        },
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
            "flag": "--validate",
            "help": "Just validate the given scraper then exit.",
            "action": "store_true",
        },
    ],
)
