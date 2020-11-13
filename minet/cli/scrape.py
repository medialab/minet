# =============================================================================
# Minet Scrape CLI Action
# =============================================================================
#
# Logic of the scrape action.
#
import csv
import gzip
import codecs
import ndjson
import casanova
from collections import namedtuple
from os.path import basename
from multiprocessing import Pool
from tqdm import tqdm

from minet.utils import load_definition
from minet.scrape import scrape, headers_from_definition
from minet.cli.utils import (
    open_output_file,
    die,
    create_glob_iterator,
    create_report_iterator,
    LazyLineDict
)

ScrapeWorkerResult = namedtuple(
    'ScrapeWorkerResult',
    ['error', 'items']
)


def worker(payload):
    row, headers, path, encoding, content, scraper = payload

    # Reading from file
    if content is None:
        try:
            if path.endswith('.gz'):
                with open(path, 'rb') as f:
                    content_bytes = gzip.decompress(f.read())

                content = content_bytes.decode(encoding, errors='replace')
            else:
                with codecs.open(path, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
        except UnicodeDecodeError as e:
            return ScrapeWorkerResult(e, None)

    # Building context
    context = {}

    if row:
        context['line'] = LazyLineDict(headers, row)

    if path:
        context['path'] = path
        context['basename'] = basename(path)

    # Attempting to scrape
    items = scrape(scraper, content, context=context)

    return ScrapeWorkerResult(None, items)


def scrape_action(namespace):

    output_file = open_output_file(namespace.output)

    # Parsing scraper definition
    try:
        scraper = load_definition(namespace.scraper)
    except TypeError:
        die([
            'Unknown scraper format.',
            'Expecting a JSON or YAML file.'
        ])
    except:
        die('Invalid scraper file.')

    if namespace.format == 'csv':
        output_headers = headers_from_definition(scraper)
        output_writer = csv.DictWriter(output_file, fieldnames=output_headers)
        output_writer.writeheader()
    else:
        output_writer = ndjson.writer(output_file)

    loading_bar = tqdm(
        desc='Scraping pages',
        total=namespace.total,
        dynamic_ncols=True,
        unit=' pages'
    )

    loading_bar.set_postfix(p=namespace.processes)

    if namespace.glob is not None:
        files = create_glob_iterator(namespace, scraper)
    else:
        reader = casanova.reader(namespace.report)
        files = create_report_iterator(namespace, reader, scraper, loading_bar)

    with Pool(namespace.processes) as pool:
        for error, items in pool.imap_unordered(worker, files):
            loading_bar.update()

            if not isinstance(items, list):
                items = [items]

            for item in items:
                if not isinstance(item, dict):
                    item = {'value': item}

                output_writer.writerow(item)

    output_file.close()
