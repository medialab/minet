# =============================================================================
# Minet Extract Content CLI Action
# =============================================================================
#
# Logic of the extract action.
#
from typing import Optional, List, Dict, Iterator, Any

from os.path import isdir
from trafilatura.core import bare_extraction
from dataclasses import dataclass
from itertools import count
from casanova import TabularRecord, Enricher

from minet.multiprocessing import LazyPool
from minet.fs import read_potentially_gzipped_path
from minet.cli.utils import (
    create_fetch_like_report_iterator,
    with_enricher_and_loading_bar,
)
from minet.cli.console import console
from minet.cli.reporters import report_error
from minet.exceptions import TrafilaturaError
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
    meta: Optional[Dict[str, Any]] = None


@dataclass
class ExtractAddendum(TabularRecord):
    extract_error: Optional[str] = None
    canonical_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    comments: Optional[str] = None
    author: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    date: Optional[str] = None
    sitename: Optional[str] = None


def plural(meta: Dict[str, Any], key: str) -> List[str]:
    l = meta.get(key, []) or []

    items = []

    if not l:
        return items

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

    return items


def worker(payload: ExtractWorkerPayload) -> ExtractResult:
    text = payload.text

    result = ExtractResult(id=payload.id)

    # Reading file
    if text is None:
        try:
            text = read_potentially_gzipped_path(
                payload.path, encoding=payload.encoding
            )
        except (FileNotFoundError, UnicodeDecodeError) as e:
            result.error = e
            return result

    # Attempting extraction
    try:
        # https://trafilatura.readthedocs.io/en/latest/corefunctions.html
        # TODO: discuss deduplication
        # TODO: fallback options
        result.meta = bare_extraction(text)
    except Exception as e:
        result.error = TrafilaturaError(reason=e)
        return result

    return result


@with_enricher_and_loading_bar(
    headers=ExtractAddendum,
    title="Extracting text",
    unit="docs",
)
def action(cli_args, enricher: Enricher, loading_bar):
    if cli_args.input_dir is not None and not isdir(cli_args.input_dir):
        raise FatalError(
            'Could not find the [cyan]-I/--input-dir "{}"[/cyan] directory!'.format(
                cli_args.input_dir
            )
        )

    items = create_fetch_like_report_iterator(cli_args, enricher)

    worked_on: Dict[int, List[str]] = {}

    def payloads() -> Iterator[ExtractWorkerPayload]:
        current_id = count()

        for item in items:

            # Items we cannot process
            if item.error is not None:
                loading_bar.advance()
                loading_bar.inc_stat(item.error, style="error")
                enricher.writerow(item.row)
                continue

            item_id = next(current_id)

            worked_on[item_id] = item.row

            yield ExtractWorkerPayload(
                id=item_id, encoding=item.encoding, path=item.path, text=item.text
            )

    pool = LazyPool(cli_args.processes)

    loading_bar.set_title("Extracting text (p=%i)" % pool.processes)

    warned_about_input_dir = False

    with pool:
        for result in pool.imap_unordered(
            worker, payloads(), chunksize=cli_args.chunk_size
        ):
            with loading_bar.step():
                assert isinstance(result, ExtractResult)

                row = worked_on.pop(result.id)

                if result.error is not None:
                    error_code = report_error(result.error)
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

                    addendum = ExtractAddendum(extract_error=error_code)
                    enricher.writerow(row, addendum)

                    continue

                meta = result.meta

                if meta is None:
                    loading_bar.inc_stat("no-trafilatura-result", style="error")
                    console.warning("did you forget to use [cyan]-i/--input[/cyan]?")
                    addendum = ExtractAddendum(extract_error="no-trafilatura-result")
                else:
                    addendum = ExtractAddendum(
                        canonical_url=meta.get("url"),
                        title=meta.get("title"),
                        description=meta.get("description"),
                        content=meta.get("text"),
                        comments=meta.get("comments"),
                        author=meta.get("author"),
                        categories=plural(meta, "categories"),
                        tags=plural(meta, "tags"),
                        date=meta.get("date"),
                        sitename=meta.get("sitename"),
                    )

                enricher.writerow(row, addendum)
