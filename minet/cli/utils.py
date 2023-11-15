# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
from typing import Optional, Iterable, List, Iterator

import os
import sys
import stat
import yaml
import platform
import casanova
from casanova.namedrecord import is_tabular_record_class
from dataclasses import dataclass
from glob import iglob
from copy import copy
from os.path import join, expanduser, isfile, relpath
from collections.abc import Mapping
from functools import wraps
from logging import Handler
from contextlib import nullcontext
from ebbe import format_seconds, get
from types import SimpleNamespace

from minet.crawl import CrawlerState
from minet.encodings import is_supported_encoding
from minet.cli.console import console
from minet.cli.loading_bar import LoadingBar, StatsItem
from minet.cli.exceptions import FatalError
from minet.utils import fuzzy_int, message_flatmap


def colored(string, color):
    return "[{color}]{string}[/{color}]".format(string=string, color=color)


def redirect_to_devnull():
    # Taken from: https://docs.python.org/3/library/signal.html
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())


def with_cli_exceptions(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)

        except KeyboardInterrupt:
            redirect_to_devnull()
            sys.exit(1)

        except BrokenPipeError:
            console.print(
                "[warning]minet process was stopped because piped command exited!"
            )
            redirect_to_devnull()
            sys.exit(1)

        except Exception:
            console.print("[error]minet process was stopped because an error occurred!")
            raise

    return wrapper


def get_stdin_status():
    mode = os.fstat(sys.stdin.fileno()).st_mode

    if stat.S_ISFIFO(mode):
        return "piped"
    elif stat.S_ISREG(mode):
        return "redirected"

    return "terminal"


def is_stdin_empty():
    return not sys.stdin.buffer.peek(1)


def was_piped_something():
    return get_stdin_status() != "terminal" and not is_stdin_empty()


def print_err(*messages):
    print(message_flatmap(*messages), file=sys.stderr)


def die(*messages):
    print_err(*messages)

    sys.exit(1)


def safe_index(l, e):
    try:
        return l.index(e)
    except ValueError:
        return None


class CLIRetryerHandler(Handler):
    def emit(self, record):
        if record.source == "request_retryer":
            exc = record.exception
            pretty_time = format_seconds(record.sleep_time)

            exc_name = "%s.%s" % (exc.__class__.__module__, exc.__class__.__name__)
            exc_msg = str(exc)

            msg = [
                "%s now wait for %s because of following exception:"
                % ("A thread will" if record.from_thread else "Will", pretty_time),
                exc_name,
            ]

            if exc_msg:
                msg.append("Exception message: %s" % exc_msg)

            if record.epilog:
                msg.append("[dim]%s[/dim]" % record.epilog)

            msg.append("")

        else:
            msg = [record.msg, ""]

        console.log_with_time("\n".join(msg), style="warning")


class CLIDownloaderHandler(Handler):
    def emit(self, record):
        console.info(record.msg)


def acquire_cross_platform_stdout():
    # As per #254: stdout need to be wrapped so that windows get a correct csv
    # stream output
    # As per #905: powershell sometimes writes a UTF-16-LE BOM in the stdout
    # before one has any chance to reconfigure the stream as UTF-8
    # Reference: https://stackoverflow.com/questions/68487529/how-to-ensure-python-prints-utf-8-and-not-utf-16-le-when-piped-in-powershell
    if "windows" in platform.system().lower():
        console.vprint(
            [
                "You piped the result of your command into stdout.",
                'Stdout piping (">") is known to be unreliable on Windows shells (cmd.exe, PowerShell)',
                "and can sometimes result in corrupted data.",
                "",
                "Are you sure you know what you are doing?",
                "If you are not sure, please use the --output flag instead.",
                "",
            ],
            style="warning",
        )

        # As per #497: we reconfigure the stdout to be UTF-8 on
        # windows
        sys.__stdout__.reconfigure(encoding="utf-8")
        sys.__stderr__.reconfigure(encoding="utf-8")

        return open(
            sys.__stdout__.fileno(),
            mode=sys.__stdout__.mode,
            buffering=1,
            encoding=sys.__stdout__.encoding,
            errors=sys.__stdout__.errors,
            newline="",
            closefd=False,
        )

    return sys.stdout


@dataclass
class FetchReportLikeItem:
    index: int
    row: List[str]
    path: Optional[str] = None
    encoding: Optional[str] = None
    text: Optional[str] = None
    error: Optional[str] = None
    url: Optional[str] = None


def create_fetch_like_report_iterator(
    cli_args: SimpleNamespace, reader: casanova.Reader
) -> Iterator[FetchReportLikeItem]:
    headers = reader.headers
    input_dir = cli_args.input_dir or ""

    # TODO: deal with no_headers
    assert headers is not None

    url_column = getattr(cli_args, "url_column", None)

    path_pos = headers.get(cli_args.column) if cli_args.column is not None else None
    error_pos = headers.get(cli_args.error_column)
    status_pos = headers.get(cli_args.status_column)
    encoding_pos = headers.get(cli_args.encoding_column)
    mimetype_pos = headers.get(cli_args.mimetype_column)
    body_pos = headers.get(cli_args.body_column)
    url_pos = headers.get(url_column) if url_column is not None else None

    for i, row in reader.enumerate():
        item = FetchReportLikeItem(index=i, row=row)

        item.url = getattr(cli_args, "base_url", None)

        if url_pos is not None:
            url = get(row, url_pos, "").strip()

            if url:
                item.url = url

        if error_pos is not None:
            error = get(row, error_pos, "").strip()

            if error:
                item.error = "http-errored"
                yield item
                continue

        if status_pos is not None:
            status = get(row, status_pos)

            if status:
                status = fuzzy_int(status)

            if status != 200:
                item.error = "invalid-status"
                yield item
                continue

        if mimetype_pos is not None:
            mimetype = get(row, mimetype_pos, "text/html").strip()

            if "/htm" not in mimetype:
                item.error = "invalid-mimetype"
                yield item
                continue

        if path_pos is not None:
            path = get(row, path_pos, "").strip()

            if path:
                item.path = join(input_dir, path)

        if body_pos is not None:
            body = get(row, body_pos)

            if body is not None:
                item.text = body

        if item.path is None and item.text is None:
            item.error = "no-path-nor-body"
            yield item
            continue

        # NOTE: can be None, which means we will guess
        item.encoding = cli_args.encoding

        if encoding_pos is not None:
            encoding = get(row, encoding_pos, "").strip()

            if encoding:
                if not is_supported_encoding(encoding):
                    item.error = "encoding-not-supported"
                    yield item
                    continue

                item.encoding = encoding

        if cli_args.glob:
            for p in iglob(item.path, recursive=True):
                new_item = copy(item)
                new_item.path = relpath(p, start=input_dir)
                yield new_item

            continue

        yield item


def get_rcfile(rcfile_path=None):
    home = expanduser("~")

    files = [
        rcfile_path,
        ".minetrc",
        ".minetrc.yml",
        ".minetrc.yaml",
        ".minetrc.json",
        join(home, ".minetrc"),
        join(home, ".minetrc.yml"),
        join(home, ".minetrc.yaml"),
        join(home, ".minetrc.json"),
    ]

    for p in files:
        if p is None or not isfile(p):
            continue

        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)

    return None


def with_fatal_errors(mapping_or_hook):
    if not isinstance(mapping_or_hook, Mapping) and not callable(mapping_or_hook):
        raise TypeError("Expecting mapping or callable")

    def decorate(action):
        @wraps(action)
        def wrapper(*args, **kwargs):
            try:
                return action(*args, **kwargs)
            except Exception as e:
                msg = None

                if isinstance(mapping_or_hook, Mapping):
                    msg = mapping_or_hook.get(type(e))
                elif callable(mapping_or_hook):
                    msg = mapping_or_hook(args[0], e)

                if msg is not None:
                    raise FatalError(msg)

                raise e

        return wrapper

    return decorate


def with_loading_bar(stats: Optional[Iterable[StatsItem]] = None, **loading_bar_kwargs):
    def decorate(action):
        @wraps(action)
        def wrapper(cli_args, *args, **kwargs):
            total = getattr(cli_args, "total", None)

            with LoadingBar(
                total=total,
                stats=stats,
                refresh_per_second=getattr(cli_args, "refresh_per_second", 10),
                simple=getattr(cli_args, "simple_progress", False),
                **loading_bar_kwargs
            ) as loading_bar:
                additional_kwargs = {
                    "loading_bar": loading_bar,
                }

                return action(cli_args, *args, **additional_kwargs, **kwargs)

        return wrapper

    return decorate


def with_enricher_and_loading_bar(
    headers,
    enricher_type=None,
    get_input=None,
    index_column: Optional[str] = None,
    #
    title=None,
    unit: Optional[str] = None,
    sub_unit: Optional[str] = None,
    stats: Optional[Iterable[StatsItem]] = None,
    stats_sort_key=None,
    nested: bool = False,
    show_label: bool = False,
    total_from_enricher: bool = True,
):
    def decorate(action):
        @wraps(action)
        def wrapper(cli_args, *args, **kwargs):
            enricher_context = nullcontext()

            # Do we need to display a transient resume progress?
            if (
                hasattr(cli_args, "resume")
                and cli_args.resume
                and isinstance(
                    cli_args.output,
                    (casanova.RowCountResumer, casanova.ThreadSafeResumer),
                )
                and cli_args.output.can_resume()
            ):
                resume_loading_bar = LoadingBar(
                    title="Reading output to resume",
                    unit="lines",
                    transient=True,
                    refresh_per_second=getattr(cli_args, "refresh_per_second", 10),
                    simple=getattr(cli_args, "simple_progress", False),
                )
                enricher_context = resume_loading_bar

                def listener(event, _):
                    if event == "output.row.read":
                        resume_loading_bar.advance()

                cli_args.output.set_listener(listener)

            enricher_fn = casanova.enricher

            if enricher_type == "threadsafe":
                enricher_fn = casanova.threadsafe_enricher

            elif enricher_type == "batch":
                enricher_fn = casanova.batch_enricher

            elif enricher_type is not None:
                raise TypeError("wrong enricher type")

            enricher_kwargs = {}

            if index_column is not None:
                enricher_kwargs["index_column"] = index_column

            multiplex = None

            if getattr(cli_args, "explode", None) is not None:
                multiplex = casanova.Multiplexer(cli_args.column, cli_args.explode)

            with enricher_context:
                enricher = enricher_fn(
                    cli_args.input if not callable(get_input) else get_input(cli_args),
                    cli_args.output,
                    add=headers(cli_args)
                    if callable(headers) and not is_tabular_record_class(headers)
                    else headers,
                    select=cli_args.select,
                    total=getattr(cli_args, "total", None),
                    multiplex=multiplex,
                    **enricher_kwargs
                )

            completed = 0

            if isinstance(cli_args.output, casanova.Resumer):
                try:
                    completed = cli_args.output.already_done_count()
                except NotImplementedError:
                    pass

            with LoadingBar(
                title=title(cli_args) if callable(title) else title,
                total=enricher.total if total_from_enricher else None,
                unit=unit(cli_args) if callable(unit) else unit,
                sub_unit=sub_unit(cli_args) if callable(sub_unit) else sub_unit,
                nested=nested,
                stats=stats,
                stats_sort_key=stats_sort_key,
                show_label=show_label,
                completed=completed,
                refresh_per_second=getattr(cli_args, "refresh_per_second", 10),
                simple=getattr(cli_args, "simple_progress", False),
            ) as loading_bar:
                additional_kwargs = {
                    "enricher": enricher,
                    "loading_bar": loading_bar,
                }

                return action(cli_args, *args, **additional_kwargs, **kwargs)

        return wrapper

    return decorate


def with_ctrl_c_warning(fn):
    def wrapper(cli_args, loading_bar, **kwargs):
        try:
            fn(cli_args, loading_bar=loading_bar, **kwargs)
        except KeyboardInterrupt:
            loading_bar.cursor_up()
            loading_bar.stop()
            console.print("Performing clean shutdown by cancelling ongoing calls...")
            console.print("This may take some seconds if you are hitting slow servers.")
            console.print("Ctrl-C again if you want to force exit.")
            raise

    return wrapper


def track_crawler_state_with_loading_bar(
    loading_bar: LoadingBar, crawler_state: CrawlerState
) -> None:
    def on_state_update(state: CrawlerState):
        loading_bar.set_total(state.total)
        loading_bar.set_stat("queued", state.jobs_queued)
        loading_bar.set_stat("doing", state.jobs_doing)
        loading_bar.set_stat("done", state.jobs_done)

    crawler_state.set_listener(on_state_update)
