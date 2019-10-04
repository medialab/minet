# =============================================================================
# Minet Scrape CLI Action
# =============================================================================
#
# Logic of the scrape action.
#
import csv
import json
import yaml
import sys
import codecs
from glob import iglob
from collections import namedtuple
from os.path import join, basename
from multiprocessing import Pool
from tqdm import tqdm
from yaml import Loader as YAMLLoader

from minet.scrape import scrape, headers_from_definition
from minet.cli.utils import custom_reader, DummyTqdmFile, die, JSONLWriter

ERROR_REPORTERS = {
    UnicodeDecodeError: 'wrong-encoding'
}

ScrapeWorkerPayload = namedtuple(
    'ScrapeWorkerPayload',
    ['scraper', 'line', 'path', 'encoding', 'content']
)

ScrapeWorkerResult = namedtuple(
    'ScrapeWorkerResult',
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
                return ScrapeWorkerResult(e, None)

    # Building context
    context = {}

    if line:
        context['line'] = line

    if path:
        context['path'] = path
        context['basename'] = basename(path)

    # Attempting to scrape
    items = scrape(scraper, content, context=context)

    return ScrapeWorkerResult(None, items)


def create_report_iterator(namespace, loading_bar, scraper):
    input_headers, pos, reader = custom_reader(namespace.report, ('status', 'filename', 'encoding', 'raw_content'))

    for line in reader:
        status = int(line[pos.status]) if line[pos.status] else None
        filename = line[pos.filename]

        if (
            status is None or
            status >= 400 or
            not filename
        ):
            loading_bar.update()
            continue

        if pos.raw_content is not None:
            yield ScrapeWorkerPayload(
                scraper,
                line,
                path=None,
                encoding=None,
                content=line[pos.raw_content]
            )

            continue

        path = join(namespace.input_directory, filename)
        encoding = line[pos.encoding].strip() or 'utf-8'

        yield ScrapeWorkerPayload(
            scraper,
            line,
            path=path,
            encoding=encoding,
            content=None
        )


def create_glob_iterator(namespace, scraper):
    for p in iglob(namespace.glob, recursive=True):
        yield ScrapeWorkerPayload(
            scraper,
            line=None,
            path=p,
            encoding='utf-8',
            content=None
        )


def scrape_action(namespace):

    if namespace.output is None:
        output_file = DummyTqdmFile(sys.stdout)
    else:
        output_file = open(namespace.output, 'w')

    # Parsing scraper definition
    scraper_name = namespace.scraper.name

    if scraper_name.endswith('.json'):
        scraper = json.load(namespace.scraper)
    elif scraper_name.endswith('.yml') or scraper_name.endswith('.yaml'):
        scraper = yaml.load(namespace.scraper, Loader=YAMLLoader)
    else:
        die([
            'Unknown scraper format.',
            'Expecting a JSON or YAML file.'
        ])

    if namespace.format == 'csv':
        output_headers = headers_from_definition(scraper)
        output_writer = csv.DictWriter(output_file, fieldnames=output_headers)
        output_writer.writeheader()
    else:
        output_writer = JSONLWriter(output_file)

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
        files = create_report_iterator(namespace, loading_bar, scraper)

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
