# =============================================================================
# Minet Scrape CLI Action
# =============================================================================
#
# Logic of the scrape action.
#
import csv
import sys
import codecs
import warnings
from os.path import join
from multiprocessing import Pool
from tqdm import tqdm

from minet.scrape import scrape
from minet.cli.utils import custom_reader, DummyTqdmFile

ERROR_REPORTERS = {
    UnicodeDecodeError: 'wrong-encoding'
}


def worker(payload):

    line, path, encoding = payload

    # Reading file
    with codecs.open(path, 'r', encoding=encoding, errors='replace') as f:
        try:
            raw_html = f.read()
        except UnicodeDecodeError as e:
            return e, line, None

    # Attempting extraction
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            content = extract_content(raw_html)
    except BaseException as e:
        # TODO: I don't know yet what can happen
        raise

    return None, line, content


def scrape_action(namespace):
    input_headers, pos, reader = custom_reader(namespace.report, ('status', 'filename', 'encoding'))

    if namespace.output is None:
        output_file = DummyTqdmFile(sys.stdout)
    else:
        output_file = open(namespace.output, 'w')

    output_writer = csv.writer(output_file)
    # output_writer.writerow(output_headers)

    def files():
        for line in reader:
            status = int(line[pos.status]) if line[pos.status] else None

            if status is None or status >= 400:
                output_writer.writerow(line)
                loading_bar.update()
                continue

            path = join(namespace.input_directory, line[pos.filename])
            encoding = line[pos.encoding].strip() or 'utf-8'

            yield line, path, encoding

    loading_bar = tqdm(
        desc='Scraping pages',
        total=namespace.total,
        dynamic_ncols=True,
        unit=' pages'
    )

    with Pool(namespace.processes) as pool:
        for error, line, items in pool.imap_unordered(worker, files()):
            loading_bar.update()

            loading_bar.write(items)

    output_file.close()
