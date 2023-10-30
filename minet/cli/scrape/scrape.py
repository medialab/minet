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
from os.path import basename, isdir

from minet.scrape import Scraper
from minet.scrape.typical import TYPICAL_SCRAPERS
from minet.scrape.types import ScraperBase
from minet.multiprocessing import LazyPool
from minet.exceptions import (
    DefinitionInvalidFormatError,
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
FORMAT: Optional[str] = None
PLURAL_SEPARATOR: Optional[str] = None
HEADERS: Optional[casanova.headers] = None


def init_process(options):
    global SCRAPER
    global FORMAT
    global PLURAL_SEPARATOR
    global HEADERS

    if options["name"] is not None:
        SCRAPER = TYPICAL_SCRAPERS[options["name"]]()
    else:
        SCRAPER = Scraper(options["definition"], strain=options["strain"])

    FORMAT = options["format"]
    PLURAL_SEPARATOR = options["plural_separator"]
    HEADERS = casanova.headers(options["fieldnames"])


def worker(payload: ScrapeWorkerPayload) -> ScrapeResult:
    assert SCRAPER is not None
    assert PLURAL_SEPARATOR is not None
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
    if FORMAT == "csv":
        items = SCRAPER.as_csv_rows(
            text, context=context, plural_separator=PLURAL_SEPARATOR
        )
    else:
        items = SCRAPER.as_records(text, context=context)

    # NOTE: errors might be raised when we consume the generators created above
    try:
        items = list(items)
    except (ScraperEvalError, ScraperEvalTypeError, ScraperEvalNoneError) as error:
        result.error = error
        return result

    result.items = items

    return result


def action(cli_args):
    using_typical_scraper = False

    # Parsing scraper definition
    try:
        if cli_args.scraper in TYPICAL_SCRAPERS:
            using_typical_scraper = True
            scraper = TYPICAL_SCRAPERS[cli_args.scraper]()
        else:
            scraper = Scraper(cli_args.scraper, strain=cli_args.strain)

    except DefinitionInvalidFormatError:
        raise FatalError(
            ["Unknown scraper format!", "It should be a JSON or YAML file."]
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

    if scraper.fieldnames is None and cli_args.format == "csv":
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

    if cli_args.format == "csv":
        assert scraper.fieldnames is not None

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
            enricher.writerow(row, item)

    else:
        # TODO: casanova should probably expose some ndjson enricher
        reader = casanova.reader(cli_args.input, total=cli_args.total)
        writer = ndjson.writer(cli_args.output)

        def writerow(row, item):
            writer.writerow(item)

    with LoadingBar(
        "Scraping", unit="pages", total=reader.total if not cli_args.glob else None
    ) as loading_bar:
        items = create_fetch_like_report_iterator(cli_args, reader)

        worked_on: Dict[int, FetchReportLikeItem] = {}

        def payloads() -> Iterator[ScrapeWorkerPayload]:
            current_id = count()

            for item in items:
                # Items we cannot process
                if item.error is not None:
                    loading_bar.advance()
                    loading_bar.inc_stat(item.error, style="error")

                    # NOTE: we emit an empty line on error if scraper is singular
                    writerow(item.row, None)
                    continue

                item_id = next(current_id)

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
            initargs=(
                {
                    "name": cli_args.scraper if using_typical_scraper else None,
                    "definition": getattr(scraper, "definition", None),
                    "strain": cli_args.strain if not using_typical_scraper else None,
                    "format": cli_args.format,
                    "plural_separator": cli_args.plural_separator,
                    "fieldnames": reader.fieldnames,
                },
            ),
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
                    original_item = worked_on.pop(result.id)

                    if result.error is not None:
                        # NOTE: we emit an empty line on error if scraper is singular
                        if is_singular:
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

                    for item in items:
                        writerow(original_item.row, item)

                    # NOTE: we emit an empty line for singular scraper if no match occurred
                    if is_singular and not items:
                        writerow(original_item.row, None)

                    loading_bar.inc_stat(
                        "scraped-items", count=len(items), style="info"
                    )
