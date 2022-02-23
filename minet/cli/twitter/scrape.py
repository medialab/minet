# =============================================================================
# Minet Scrape CLI Action
# =============================================================================
#
# Logic of the scrape action.
#
import csv
import sys
import ndjson
import casanova
from casanova import DictLikeRow
from termcolor import colored
from collections import namedtuple
from os.path import basename, isdir

from minet import Scraper
from minet.multiprocessing import LazyPool
from minet.exceptions import (
    DefinitionInvalidFormatError,
)
from minet.scrape.exceptions import (
    InvalidScraperError,
    CSSSelectorTooComplex,
    ScraperEvalError,
    ScraperEvalTypeError,
    ScraperEvalNoneError
)
from minet.cli.reporters import (
    report_scraper_validation_errors,
    report_scraper_evaluation_error
)
from minet.fs import read_potentially_gzipped_path
from minet.cli.utils import (
    die,
    dummy_csv_file_from_glob,
    create_report_iterator,
    LoadingBar
)
from minet.cli.constants import DEFAULT_CONTENT_FOLDER

ScrapeWorkerResult = namedtuple(
    'ScrapeWorkerResult',
    ['error', 'items']
)

PROCESS_SCRAPER = None


def init_process(definition, strain):
    global PROCESS_SCRAPER

    PROCESS_SCRAPER = Scraper(definition, strain=strain)


def worker(payload):
    row, headers, path, encoding, content, args = payload
    output_format, plural_separator = args

    # Reading from file
    if content is None:
        try:
            content = read_potentially_gzipped_path(path, encoding=encoding)
        except (FileNotFoundError, UnicodeDecodeError) as e:
            return ScrapeWorkerResult(e, None)

    # Building context
    context = {}

    if row:
        context['line'] = DictLikeRow(headers, row)

    if path:
        context['path'] = path
        context['basename'] = basename(path)

    # Attempting to scrape
    if output_format == 'csv':
        items = PROCESS_SCRAPER.as_csv_dict_rows(content, context=context, plural_separator=plural_separator)
    else:
        items = PROCESS_SCRAPER.as_records(content, context=context)

    # NOTE: errors will only be raised when we consume the generators created above
    try:
        items = list(items)
    except (ScraperEvalError, ScraperEvalTypeError, ScraperEvalNoneError) as error:
        return ScrapeWorkerResult(error, None)

    return ScrapeWorkerResult(None, items)


def scrape_action(cli_args):
    if cli_args.glob is None and cli_args.input_dir is None:
        cli_args.input_dir = DEFAULT_CONTENT_FOLDER

    # Parsing scraper definition
    try:
        scraper = Scraper(cli_args.scraper, strain=cli_args.strain)
    except DefinitionInvalidFormatError:
        die([
            'Unknown scraper format!',
            'It should be a JSON or YAML file.'
        ])
    except FileNotFoundError:
        die('Could not find scraper file!')
    except InvalidScraperError as error:
        print('Your scraper is invalid! You need to fix the following errors:', file=sys.stderr)
        print(file=sys.stderr)
        sys.stderr.write(report_scraper_validation_errors(error.validation_errors))
        die()
    except CSSSelectorTooComplex:
        die([
            'Your strainer\'s CSS selector %s is too complex.' % colored(cli_args.strain, 'blue'),
            'You cannot use relations to create a strainer.',
            'Try to simplify the selector you passed to --strain.'
        ])

    if cli_args.validate:
        print('Your scraper is valid.', file=sys.stderr)
        sys.exit(0)

    if scraper.headers is None and cli_args.format == 'csv':
        die([
            'Your scraper does not yield tabular data.',
            'Try changing it or setting --format to "jsonl".'
        ])

    loading_bar = LoadingBar(
        desc='Scraping pages',
        total=cli_args.total,
        unit='page'
    )

    worker_args = (
        cli_args.format,
        cli_args.separator
    )

    def on_irrelevant_row(reason, row, i):
        loading_bar.print('Row n°{n} could not be processed: {reason}'.format(n=i + 1, reason=reason))
        loading_bar.update()

    input_data = cli_args.report

    if cli_args.glob is not None:
        input_data = dummy_csv_file_from_glob(cli_args.glob, cli_args.input_dir)

    reader = casanova.reader(input_data)

    if (
        cli_args.glob is None and
        'raw_contents' not in reader.headers and
        not isdir(cli_args.input_dir)
    ):
        loading_bar.die([
            'Could not find the "%s" directory!' % cli_args.input_dir,
            'Did you forget to specify it with -i/--input-dir?'
        ])

    files = create_report_iterator(
        cli_args,
        reader,
        worker_args=worker_args,
        on_irrelevant_row=on_irrelevant_row
    )

    if cli_args.format == 'csv':
        output_writer = csv.DictWriter(cli_args.output, fieldnames=scraper.headers)
        output_writer.writeheader()
    else:
        output_writer = ndjson.writer(cli_args.output)

    pool = LazyPool(
        cli_args.processes,
        initializer=init_process,
        initargs=(scraper.definition, cli_args.strain)
    )

    loading_bar.update_stats(p=pool.processes)

    with pool:
        for error, items in pool.imap_unordered(worker, files):
            loading_bar.update()

            if error is not None:
                if isinstance(error, (ScraperEvalError, ScraperEvalTypeError, ScraperEvalNoneError)):
                    loading_bar.print(report_scraper_evaluation_error(error), end='')
                else:
                    loading_bar.print(error, repr(error))
                loading_bar.inc('errors')
                continue

            for item in items:
                output_writer.writerow(item)
