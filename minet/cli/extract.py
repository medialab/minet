# =============================================================================
# Minet Extract Content CLI Action
# =============================================================================
#
# Logic of the extract action.
#
import casanova
from trafilatura.core import bare_extraction

from minet.multiprocessing import LazyPool
from minet.encodings import is_supported_encoding
from minet.fs import read_potentially_gzipped_path
from minet.cli.utils import (
    open_output_file,
    create_report_iterator,
    LoadingBar
)
from minet.cli.reporters import report_error
from minet.exceptions import TrafilaturaError

from minet.exceptions import UnknownEncodingError

OUTPUT_ADDITIONAL_HEADERS = [
    'extract_error',
    'canonical_url',
    'title',
    'description',
    'raw_content',
    'comments',
    'author',
    'categories',
    'tags',
    'date',
    'sitename'
]

PADDING = [''] * (len(OUTPUT_ADDITIONAL_HEADERS) - 1)


def singular(result, key):
    return result.get(key, '') or ''


def plural(result, key):
    l = result.get(key, []) or []

    if not l:
        return ''

    items = []

    for item in l:
        for subitem in item.split(','):
            subitem = subitem.strip()

            if subitem:
                items.append(subitem)

    return '|'.join(items)


def format_trafilatura_result(result):
    return [
        '',
        singular(result, 'url'),
        singular(result, 'title'),
        singular(result, 'description'),
        singular(result, 'text'),
        singular(result, 'comments'),
        singular(result, 'author'),
        plural(result, 'categories'),
        plural(result, 'tags'),
        singular(result, 'date'),
        singular(result, 'sitename')
    ]


def format_error(error):
    return [error] + PADDING


def worker(payload):
    row, _, path, encoding, content, _ = payload

    if not is_supported_encoding(encoding):
        return UnknownEncodingError('Unknown encoding: "%s"' % encoding), row, None

    # Reading file
    if content is None:
        try:
            raw_html = read_potentially_gzipped_path(path, encoding=encoding)
        except (FileNotFoundError, UnicodeDecodeError) as e:
            return e, row, None
    else:
        raw_html = content

    # Attempting extraction
    try:
        # https://trafilatura.readthedocs.io/en/latest/corefunctions.html
        # TODO: discuss deduplication
        # TODO: fallback options
        result = bare_extraction(raw_html)
    except Exception as e:
        return TrafilaturaError(reason=e), row, None

    if result is None:
        return None, row, None

    return None, row, format_trafilatura_result(result)


def extract_action(namespace):
    output_file = open_output_file(namespace.output)

    enricher = casanova.enricher(
        namespace.report,
        output_file,
        keep=namespace.select,
        add=OUTPUT_ADDITIONAL_HEADERS
    )

    loading_bar = LoadingBar(
        desc='Extracting content',
        total=namespace.total,
        unit='doc'
    )

    def on_irrelevant_row(reason, row):
        loading_bar.update()
        enricher.writerow(row, format_error(reason))

    try:
        files = create_report_iterator(
            namespace,
            enricher,
            on_irrelevant_row=on_irrelevant_row
        )
    except NotADirectoryError:
        loading_bar.die([
            'Could not find the "%s" directory!' % namespace.input_dir,
            'Did you forget to specify it with -i/--input-dir?'
        ])

    pool = LazyPool(namespace.processes)

    loading_bar.update_stats(p=pool.processes)

    with pool:
        for error, row, result in pool.imap_unordered(worker, files):
            loading_bar.update()

            if error is not None:
                enricher.writerow(row, format_error(report_error(error)))
                continue

            if result is None:
                enricher.writerow(row, format_error('no-content'))
                continue

            enricher.writerow(row, result)

    loading_bar.close()
    output_file.close()
