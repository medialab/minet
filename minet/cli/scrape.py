# =============================================================================
# Minet Scrape CLI Action
# =============================================================================
#
# Logic of the scrape action.
#
import csv
import json
import sys
import codecs
from collections import namedtuple
from os.path import join
from multiprocessing import Pool
from tqdm import tqdm

from minet.scrape import scrape, headers_from_definition
from minet.cli.utils import custom_reader, DummyTqdmFile

ERROR_REPORTERS = {
    UnicodeDecodeError: 'wrong-encoding'
}

WorkerPayload = namedtuple(
    'WorkerPayload',
    ['scraper', 'line', 'path', 'encoding', 'content'],
    [None, None, None]
)

WorkerResult = namedtuple(
    'WorkerResult',
    ['error', 'items']
)


def worker(payload):
    scraper, line, path, encoding, content = payload

    # Reading from file
    if content is None:
        with codecs.open(path, 'r', encoding=encoding, errors='replace') as f:
            try:
                content = f.read()
            except UnicodeDecodeError as e:
                return WorkerResult(e, None)

    # Attempting to scrape
    items = list(scrape(content, scraper))

    return WorkerResult(None, items)


def create_report_iterator(namespace):
    input_headers, pos, reader = custom_reader(namespace.report, ('status', 'filename', 'encoding', 'raw_content'))

    for line in reader:
        status = int(line[pos.status]) if line[pos.status] else None

        if status is None or status >= 400:
            loading_bar.update()
            continue

        if pos.raw_content is not None:
            yield WorkerPayload(
                scraper,
                line,
                content=line[pos.raw_content]
            )

            continue

        path = join(namespace.input_directory, line[pos.filename])
        encoding = line[pos.encoding].strip() or 'utf-8'

        yield WorkerPayload(
            scraper,
            line,
            path=path,
            encoding=encoding,
            content=None
        )


def scrape_action(namespace):

    if namespace.output is None:
        output_file = DummyTqdmFile(sys.stdout)
    else:
        output_file = open(namespace.output, 'w')

    # Parsing scraper definition
    scraper = json.load(namespace.scraper)

    output_headers = headers_from_definition(scraper)
    output_writer = csv.DictWriter(output_file, fieldnames=output_headers)
    output_writer.writeheader()

    files = create_report_iterator(namespace)

    loading_bar = tqdm(
        desc='Scraping pages',
        total=namespace.total,
        dynamic_ncols=True,
        unit=' pages'
    )

    with Pool(namespace.processes) as pool:
        for error, items in pool.imap_unordered(worker, files()):
            loading_bar.update()

            for item in items:
                if not isinstance(item, dict):
                    item = {'value': item}

                output_writer.writerow(item)

    output_file.close()
