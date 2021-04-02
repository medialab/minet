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
from os.path import basename

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
    open_output_file,
    die,
    create_glob_iterator,
    create_report_iterator,
    LoadingBar
)

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


def scrape_action(namespace):

    output_file = open_output_file(namespace.output)

    # Parsing scraper definition
    try:
        scraper = Scraper(namespace.scraper, strain=namespace.strain)
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
            'Your strainer\'s CSS selector %s is too complex.' % colored(namespace.strain, 'blue'),
            'You cannot use relations to create a strainer.',
            'Try to simplify the selector you passed to --strain.'
        ])

    if namespace.validate:
        print('Your scraper is valid.', file=sys.stderr)
        sys.exit(0)

    if scraper.headers is None and namespace.format == 'csv':
        die([
            'Your scraper does not yield tabular data.',
            'Try changing it or setting --format to "jsonl".'
        ])

    loading_bar = LoadingBar(
        desc='Scraping pages',
        total=namespace.total,
        unit='page'
    )

    proc_args = (
        namespace.format,
        namespace.separator
    )

    def on_irrelevant_row(reason, row):
        loading_bar.update()

    if namespace.glob is not None:
        files = create_glob_iterator(namespace, proc_args)
    else:
        reader = casanova.reader(namespace.report)

        try:
            files = create_report_iterator(
                namespace,
                reader,
                args=proc_args,
                on_irrelevant_row=on_irrelevant_row
            )
        except NotADirectoryError:
            loading_bar.die([
                'Could not find the "%s" directory!' % namespace.input_dir,
                'Did you forget to specify it with -i/--input-dir?'
            ])

    if namespace.format == 'csv':
        output_writer = csv.DictWriter(output_file, fieldnames=scraper.headers)
        output_writer.writeheader()
    else:
        output_writer = ndjson.writer(output_file)

    pool = LazyPool(
        namespace.processes,
        initializer=init_process,
        initargs=(scraper.definition, namespace.strain)
    )

    loading_bar.update_stats(p=pool.processes)

    with pool:
        for error, items in pool.imap_unordered(worker, files):
            loading_bar.update()

            if error is not None:
                if isinstance(error, (ScraperEvalError, ScraperEvalTypeError, ScraperEvalNoneError)):
                    loading_bar.print(report_scraper_evaluation_error(error), end='')
                loading_bar.inc('errors')
                continue

            for item in items:
                output_writer.writerow(item)

    loading_bar.close()
    output_file.close()
