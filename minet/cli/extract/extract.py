# =============================================================================
# Minet Extract Content CLI Action
# =============================================================================
#
# Logic of the extract action.
#
from os.path import isdir
from trafilatura.core import bare_extraction

from minet.multiprocessing import LazyPool
from minet.encodings import is_supported_encoding
from minet.fs import read_potentially_gzipped_path
from minet.cli.utils import (
    create_report_iterator,
    dummy_csv_file_from_glob,
    with_enricher_and_loading_bar,
)
from minet.cli.reporters import report_error
from minet.exceptions import TrafilaturaError, UnknownEncodingError
from minet.cli.constants import DEFAULT_CONTENT_FOLDER
from minet.cli.exceptions import FatalError

OUTPUT_ADDITIONAL_HEADERS = [
    "extract_error",
    "canonical_url",
    "title",
    "description",
    "raw_content",
    "comments",
    "author",
    "categories",
    "tags",
    "date",
    "sitename",
]

PADDING = [""] * (len(OUTPUT_ADDITIONAL_HEADERS) - 1)


def singular(result, key):
    return result.get(key, "") or ""


def plural(result, key):
    l = result.get(key, []) or []

    if not l:
        return ""

    items = []

    for item in l:
        if isinstance(item, dict):
            item = item.get("name")

            if item is None:
                continue

        if isinstance(item, (int, float)):
            item = str(item)

        if not isinstance(item, str):
            continue

        for subitem in item.split(","):
            subitem = subitem.strip()

            if subitem:
                items.append(subitem)

    return "|".join(items)


def format_trafilatura_result(result):
    return [
        "",
        singular(result, "url"),
        singular(result, "title"),
        singular(result, "description"),
        singular(result, "text"),
        singular(result, "comments"),
        singular(result, "author"),
        plural(result, "categories"),
        plural(result, "tags"),
        singular(result, "date"),
        singular(result, "sitename"),
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


def get_input(cli_args):
    if cli_args.glob is not None:
        return dummy_csv_file_from_glob(cli_args.glob, cli_args.input_dir)

    return cli_args.report


@with_enricher_and_loading_bar(
    headers=OUTPUT_ADDITIONAL_HEADERS,
    get_input=get_input,
    title="Extracting content",
    unit="docs",
)
def action(cli_args, enricher, loading_bar):
    if cli_args.glob is None and cli_args.input_dir is None:
        cli_args.input_dir = DEFAULT_CONTENT_FOLDER

    def on_irrelevant_row(reason, row, i):
        loading_bar.advance()
        loading_bar.inc_stat(reason, style="error")
        enricher.writerow(row, format_error(reason))

    if (
        cli_args.glob is None
        and "raw_contents" not in enricher.headers
        and not isdir(cli_args.input_dir)
    ):
        raise FatalError(
            [
                'Could not find the "%s" directory!' % cli_args.input_dir,
                "Did you forget to specify it with -I/--input-dir?",
            ]
        )

    files = create_report_iterator(
        cli_args, enricher, on_irrelevant_row=on_irrelevant_row
    )

    pool = LazyPool(cli_args.processes)

    loading_bar.set_title("Extracting content (p=%i)" % pool.processes)

    with pool:
        for error, row, result in pool.imap_unordered(worker, files):
            loading_bar.advance()

            if error is not None:
                error_code = report_error(error)
                loading_bar.inc_stat(error_code, style="error")
                enricher.writerow(row, format_error(error_code))
                continue

            if result is None:
                loading_bar.inc_stat("no-result", style="warning")
                enricher.writerow(row, format_error("no-result"))
                continue

            enricher.writerow(row, result)
