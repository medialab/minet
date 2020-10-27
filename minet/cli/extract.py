# =============================================================================
# Minet Extract Content CLI Action
# =============================================================================
#
# Logic of the extract action.
#
import casanova
import gzip
import codecs
import warnings
from multiprocessing import Pool
from tqdm import tqdm
from dragnet import extract_content

from minet.encodings import is_supported_encoding
from minet.cli.utils import (
    open_output_file,
    create_report_iterator
)
from minet.cli.reporters import report_error

from minet.exceptions import UnknownEncodingError

OUTPUT_ADDITIONAL_HEADERS = ['extract_error', 'extracted_text']


def worker(payload):
    row, _, path, encoding, content, _ = payload

    if not is_supported_encoding(encoding):
        return UnknownEncodingError('Unknown encoding: "%s"' % encoding), row, None

    # Reading file
    if content is None:
        try:
            if path.endswith('.gz'):
                with open(path, 'rb') as f:
                    raw_html_bytes = gzip.decompress(f.read())

                raw_html = raw_html_bytes.decode(encoding, errors='replace')
            else:
                with codecs.open(path, 'r', encoding=encoding, errors='replace') as f:
                    raw_html = f.read()
        except UnicodeDecodeError as e:
            return e, row, None
    else:
        raw_html = content

    # Attempting extraction
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            content = extract_content(raw_html)
    except BaseException as e:
        return e, row, None

    return None, row, content


def extract_action(namespace):
    output_file = open_output_file(namespace.output)

    enricher = casanova.enricher(
        namespace.report,
        output_file,
        keep=namespace.select,
        add=OUTPUT_ADDITIONAL_HEADERS
    )

    loading_bar = tqdm(
        desc='Extracting content',
        total=namespace.total,
        dynamic_ncols=True,
        unit=' docs'
    )

    files = create_report_iterator(namespace, enricher, loading_bar=loading_bar)

    with Pool(namespace.processes) as pool:
        for error, row, content in pool.imap_unordered(worker, files):
            loading_bar.update()

            if error is not None:
                enricher.writerow(row, [report_error(error), ''])
                continue

            enricher.writerow(row, ['', content])

    output_file.close()
