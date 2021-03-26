# =============================================================================
# Minet Scrape CLI Action
# =============================================================================
#
# Logic of the scrape action.
#
import csv
import ndjson
import casanova
from collections import namedtuple
from os.path import basename
from multiprocessing import Pool

from minet import Scraper
from minet.exceptions import (
    DefinitionInvalidFormatError
)
from minet.cli.utils import (
    open_output_file,
    die,
    create_glob_iterator,
    create_report_iterator,
    LazyLineDict,
    LoadingBar,
    read_potentially_gzipped_path
)

ScrapeWorkerResult = namedtuple(
    'ScrapeWorkerResult',
    ['error', 'items']
)

PROCESS_SCRAPER = None


def init_process(definition):
    global PROCESS_SCRAPER

    PROCESS_SCRAPER = Scraper(definition)


def worker(payload):
    row, headers, path, encoding, content, scraper = payload

    # Reading from file
    if content is None:
        try:
            content = read_potentially_gzipped_path(path, encoding=encoding)
        except (FileNotFoundError, UnicodeDecodeError) as e:
            return ScrapeWorkerResult(e, None)

    # Building context
    context = {}

    if row:
        context['line'] = LazyLineDict(headers, row)

    if path:
        context['path'] = path
        context['basename'] = basename(path)

    # Attempting to scrape
    items = PROCESS_SCRAPER(content, context=context)

    return ScrapeWorkerResult(None, items)


def scrape_action(namespace):

    output_file = open_output_file(namespace.output)

    # Parsing scraper definition
    try:
        scraper = Scraper(namespace.scraper)
    except DefinitionInvalidFormatError:
        die([
            'Unknown scraper format!',
            'It should be a JSON or YAML file.'
        ])
    except FileNotFoundError:
        die('Could not find scraper file!')

    if namespace.format == 'csv':
        output_headers = scraper.headers
        output_writer = csv.DictWriter(output_file, fieldnames=output_headers)
        output_writer.writeheader()
    else:
        output_writer = ndjson.writer(output_file)

    loading_bar = LoadingBar(
        desc='Scraping pages',
        total=namespace.total,
        unit='page',
        stats={'p': namespace.processes}
    )

    if namespace.glob is not None:
        files = create_glob_iterator(namespace, scraper)
    else:
        reader = casanova.reader(namespace.report)

        try:
            files = create_report_iterator(namespace, reader, scraper, loading_bar)
        except NotADirectoryError:
            loading_bar.die([
                'Could not find the "%s" directory!' % namespace.input_dir,
                'Did you forget to specify it with -i/--input-dir?'
            ])

    pool = Pool(
        namespace.processes,
        initializer=init_process,
        initargs=(scraper.definition, )
    )

    with pool:
        for error, items in pool.imap_unordered(worker, files):
            loading_bar.update()

            if error is not None:
                loading_bar.inc('errors')
                continue

            if not isinstance(items, list):
                items = [items]

            for item in items:
                if not isinstance(item, dict):
                    item = {'value': item}

                output_writer.writerow(item)

    loading_bar.close()
    output_file.close()
