# =============================================================================
# Minet Extract Content CLI Action
# =============================================================================
#
# Logic of the extract action.
#
from typing import Optional, Dict, Iterator

from os.path import isdir
from dataclasses import dataclass
from itertools import count
from casanova import ThreadSafeEnricher

from minet.exceptions import TrafilaturaError
from minet.extraction import extract, TrafilaturaResult
from minet.multiprocessing import LazyPool
from minet.serialization import serialize_error_as_slug
from minet.fs import read_potentially_gzipped_path
from minet.cli.utils import (
    create_fetch_like_report_iterator,
    with_enricher_and_loading_bar,
    FetchReportLikeItem,
)
from minet.cli.console import console
from minet.cli.exceptions import FatalError


@dataclass
class ExtractWorkerPayload:
    id: int
    encoding: Optional[str]
    path: Optional[str]
    text: Optional[str]


@dataclass
class ExtractResult:
    id: int
    error: Optional[Exception] = None
    data: Optional[TrafilaturaResult] = None


def worker(payload: ExtractWorkerPayload) -> ExtractResult:
    text = payload.text

    result = ExtractResult(id=payload.id)

    # Reading file
    if text is None:
        try:
            text = read_potentially_gzipped_path(
                payload.path, encoding=payload.encoding, fallback_encoding="utf-8"
            )
        except (FileNotFoundError, UnicodeDecodeError) as e:
            result.error = e
            return result

    # Attempting extraction
    try:
        result.data = extract(text)
    except TrafilaturaError as e:
        result.error = e
        return result

    return result


HEADERS = ["extract_error"] + TrafilaturaResult.fieldnames()
PADDING = [""] * len(TrafilaturaResult.fieldnames())


@with_enricher_and_loading_bar(
    headers=HEADERS,
    enricher_type="threadsafe",
    index_column="extract_original_index",
    title="Extracting text",
    unit="docs",
    total_from_enricher=False,
)
def action(cli_args, enricher: ThreadSafeEnricher, loading_bar):
    if cli_args.input_dir is not None and not isdir(cli_args.input_dir):
        raise FatalError(
            'Could not find the [cyan]-I/--input-dir "{}"[/cyan] directory!'.format(
                cli_args.input_dir
            )
        )

    if not cli_args.glob:
        loading_bar.set_total(enricher.total)

    items = create_fetch_like_report_iterator(cli_args, enricher)

    worked_on: Dict[int, FetchReportLikeItem] = {}

    def payloads() -> Iterator[ExtractWorkerPayload]:
        current_id = count()

        for item in items:
            # Items we cannot process
            if item.error is not None:
                loading_bar.advance()
                loading_bar.inc_stat(item.error, style="error")
                enricher.writerow(item.index, item.row)
                continue

            item_id = next(current_id)

            worked_on[item_id] = item

            yield ExtractWorkerPayload(
                id=item_id, encoding=item.encoding, path=item.path, text=item.text
            )

    pool = LazyPool(cli_args.processes)

    loading_bar.append_to_title(" (p=%i)" % pool.processes)

    warned_about_input_dir = False

    with pool:
        for result in pool.imap(
            worker,
            payloads(),
            chunksize=cli_args.chunk_size,
            unordered=cli_args.unordered,
        ):
            with loading_bar.step():
                assert isinstance(result, ExtractResult)

                item = worked_on.pop(result.id)
                row = item.row

                if result.error is not None:
                    error_code = serialize_error_as_slug(result.error)
                    loading_bar.inc_stat(error_code, style="error")

                    if not warned_about_input_dir and error_code == "file-not-found":
                        warned_about_input_dir = True

                        if cli_args.input_dir is None:
                            console.warning(
                                "did you forget to give [cyan]-I/--input-dir[/cyan]? "
                            )
                        else:
                            console.warning(
                                'are you sure [cyan]-I/--input-dir "{}"[/cyan] is the correct path?'.format(
                                    cli_args.input_dir
                                )
                            )

                    enricher.writerow(item.index, row, [error_code], PADDING)

                    continue

                data = result.data

                if data is None:
                    loading_bar.inc_stat("no-trafilatura-result", style="error")
                    if not cli_args.input:
                        console.warning(
                            "did you forget to use [cyan]-i/--input[/cyan]?"
                        )

                    enricher.writerow(
                        item.index, row, ["no-trafilatura-result"], PADDING
                    )
                else:
                    enricher.writerow(item.index, row, [None], data)
