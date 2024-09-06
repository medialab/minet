# =============================================================================
# Minet Scrape CLI Action
# =============================================================================
#
# Logic of the scrape action.
#
from typing import Optional, Any, List, Dict, Iterator

import casanova
import casanova.ndjson as ndjson
from dataclasses import dataclass
from itertools import count
from threading import Lock
from os.path import basename, isdir

from minet.utils import import_target
from minet.scrape.classes import (
    NAMED_SCRAPERS,
    ScraperBase,
    DefinitionScraper,
    FunctionScraper,
)
from minet.multiprocessing import LazyPool
from minet.exceptions import (
    DefinitionInvalidFormatError,
    GenericModuleNotFoundError,
    TargetInGenericModuleNotFoundError,
)
from minet.scrape.exceptions import (
    InvalidScraperError,
    CSSSelectorTooComplex,
    ScraperEvalError,
    ScraperEvalTypeError,
    ScraperEvalNoneError,
)
from minet.cli.reporters import (
    report_scraper_validation_errors,
    report_scraper_evaluation_error,
)
from minet.serialization import serialize_error_as_slug
from minet.fs import read_potentially_gzipped_path
from minet.cli.console import console
from minet.cli.loading_bar import LoadingBar
from minet.cli.utils import create_fetch_like_report_iterator, FetchReportLikeItem
from minet.cli.exceptions import FatalError


@dataclass
class ScrapeWorkerPayload:
    id: int
    row: List[str]
    path: Optional[str]
    encoding: Optional[str]
    text: Optional[str]
    url: Optional[str]


@dataclass
class ScrapeResult:
    id: int
    error: Optional[Exception] = None
    items: Optional[Any] = None


SCRAPER: Optional[ScraperBase] = None
HEADERS: Optional[casanova.headers] = None


def init_process(scraper: ScraperBase, fieldnames: List[str]):
    global SCRAPER
    global HEADERS

    SCRAPER = scraper
    HEADERS = casanova.headers(fieldnames)


def worker(payload: ScrapeWorkerPayload) -> ScrapeResult:
    assert SCRAPER is not None
    assert HEADERS is not None

    text = payload.text

    result = ScrapeResult(id=payload.id)

    # Reading file
    if text is None:
        try:
            text = read_potentially_gzipped_path(
                payload.path, encoding=payload.encoding, fallback_encoding="utf-8"
            )
        except (FileNotFoundError, UnicodeDecodeError) as e:
            result.error = e
            return result

    # Building context
    row = HEADERS.wrap(payload.row, transient=True)
    context: Dict[str, Any] = {"row": row}

    if payload.url:
        context["url"] = payload.url

    if payload.path:
        context["path"] = payload.path
        context["basename"] = basename(payload.path)

    # Attempting to scrape
    items = SCRAPER.items(text, context=context)

    # NOTE: errors might be raised when we consume the generators created above
    try:
        items = list(items)
    except (ScraperEvalError, ScraperEvalTypeError, ScraperEvalNoneError) as error:
        result.error = error
        return result

    result.items = items

    return result


def action(cli_args):
    # Parsing scraper definition
    try:
        if cli_args.module:
            fn = import_target(cli_args.scraper, default="scrape")
            scraper = FunctionScraper(fn, strain=cli_args.strain)
        elif cli_args.eval:
            scraper = FunctionScraper(cli_args.scraper, strain=cli_args.strain)
        elif cli_args.scraper in NAMED_SCRAPERS:
            scraper = NAMED_SCRAPERS[cli_args.scraper]()
        else:
            scraper = DefinitionScraper(cli_args.scraper, strain=cli_args.strain)

    except GenericModuleNotFoundError:
        raise FatalError(
            [
                "Could not import %s!" % cli_args.scraper,
                "Are you sure the module exists?",
            ]
        )

    except TargetInGenericModuleNotFoundError as e:
        raise FatalError(
            [
                "Could not find the %s target in the %s module!" % (e.name, e.path),
                "Are you sure this class/function/variable exists in the module?",
            ]
        )

    except DefinitionInvalidFormatError:
        raise FatalError(
            [
                "Unknown scraper format!",
                "It should be a JSON or YAML file.",
                "Or did you forget the -m/--module flag?",
            ]
        )

    except FileNotFoundError:
        raise FatalError("Could not find scraper file!")

    except InvalidScraperError as error:
        raise FatalError(
            [
                "Your scraper is invalid! You need to fix the following errors:\n",
                report_scraper_validation_errors(error.validation_errors),
            ]
        )

    except CSSSelectorTooComplex:
        raise FatalError(
            [
                "Your strainer's CSS selector [info]%s[/info] is too complex."
                % cli_args.strain,
                "You cannot use relations to create a strainer.",
                "Try to simplify the selector you passed to --strain.",
            ]
        )

    if not scraper.tabular and cli_args.format == "csv":
        raise FatalError(
            [
                "Your scraper does not yield tabular data.",
                'Try changing it or setting --format to "jsonl".',
            ]
        )

    if cli_args.input_dir is not None and not isdir(cli_args.input_dir):
        raise FatalError(
            'Could not find the [cyan]-I/--input-dir "{}"[/cyan] directory!'.format(
                cli_args.input_dir
            )
        )

    writer_lock = Lock()

    if cli_args.format == "csv":
        if isinstance(scraper, FunctionScraper):
            enricher = casanova.inferring_enricher(
                cli_args.input,
                cli_args.output,
                total=cli_args.total,
                plural_separator=cli_args.plural_separator,
                select=cli_args.select,
                mapping_sample_size=512,
                buffer_optionals=True,
            )
            reader = enricher

            def writerow(row, item):
                enricher.writerow(row, item)

        else:
            assert scraper.fieldnames is not None

            serializer = casanova.CSVSerializer(
                plural_separator=cli_args.plural_separator
            )

            output_fieldnames = scraper.fieldnames

            if cli_args.scraped_column_prefix is not None:
                output_fieldnames = [
                    cli_args.scraped_column_prefix + h for h in output_fieldnames
                ]

            enricher = casanova.enricher(
                cli_args.input,
                cli_args.output,
                total=cli_args.total,
                select=cli_args.select,
                add=output_fieldnames,
            )
            reader = enricher

            def writerow(row, item):
                assert scraper.fieldnames is not None

                if item is None:
                    enricher.writerow(row)
                    return

                if isinstance(item, dict):
                    item = [item.get(f) for f in scraper.fieldnames]
                else:
                    item = [item]

                enricher.writerow(row, (serializer(v) for v in item))  # type: ignore

    else:
        # TODO: casanova should probably expose some ndjson enricher
        reader = casanova.reader(cli_args.input, total=cli_args.total)
        writer = ndjson.writer(cli_args.output)

        def writerow(row, item):
            writer.writerow(item)

    with LoadingBar(
        "Scraping", unit="pages", total=reader.total if not cli_args.glob else None
    ) as loading_bar:
        if not cli_args.has_dummy_csv and cli_args.input_dir is None:
            from minet.cli.constants import DEFAULT_CONTENT_FOLDER

            cli_args.input_dir = DEFAULT_CONTENT_FOLDER

        items = create_fetch_like_report_iterator(cli_args, reader)

        worked_on: Dict[int, FetchReportLikeItem] = {}
        worked_on_lock = Lock()

        # Fun fact: Pool.imap consumes the given iterator in a separate thread...
        def payloads() -> Iterator[ScrapeWorkerPayload]:
            current_id = count()

            for item in items:
                # Items we cannot process
                if item.error is not None:
                    loading_bar.advance()
                    loading_bar.inc_stat(item.error, style="error")

                    # NOTE: we emit an empty line on error if scraper is singular
                    if is_singular:
                        with writer_lock:
                            writerow(item.row, None)

                    continue

                item_id = next(current_id)

                with worked_on_lock:
                    worked_on[item_id] = item

                yield ScrapeWorkerPayload(
                    id=item_id,
                    encoding=item.encoding,
                    path=item.path,
                    text=item.text,
                    row=item.row,
                    url=item.url,
                )

        pool = LazyPool(
            cli_args.processes,
            initializer=init_process,
            initargs=(scraper, reader.fieldnames),
        )

        loading_bar.append_to_title(" (p=%i)" % pool.processes)

        warned_about_input_dir = False

        is_singular = scraper.singular

        with pool:
            for result in pool.imap(
                worker,
                payloads(),
                chunksize=cli_args.chunk_size,
                unordered=cli_args.unordered,
            ):
                with loading_bar.step():
                    with worked_on_lock:
                        original_item = worked_on.pop(result.id)

                    if result.error is not None:
                        # NOTE: we emit an empty line on error if scraper is singular
                        if is_singular:
                            with writer_lock:
                                writerow(original_item.row, None)

                        if isinstance(
                            result.error,
                            (
                                ScraperEvalError,
                                ScraperEvalTypeError,
                                ScraperEvalNoneError,
                            ),
                        ):
                            loading_bar.print(
                                report_scraper_evaluation_error(result.error), end=""
                            )
                        else:
                            error_code = serialize_error_as_slug(result.error)
                            loading_bar.inc_stat(error_code, style="error")

                            if (
                                not warned_about_input_dir
                                and error_code == "file-not-found"
                            ):
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

                        continue

                    # No errors
                    assert result.items is not None
                    items = result.items

                    with writer_lock:
                        for item in items:
                            writerow(original_item.row, item)

                        # NOTE: we emit an empty line for singular scraper if no match occurred
                        if is_singular and not items:
                            writerow(original_item.row, None)

                    loading_bar.inc_stat(
                        "scraped-items", count=len(items), style="info"
                    )
