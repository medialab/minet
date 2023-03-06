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

        except (KeyboardInterrupt, BrokenPipeError):
            redirect_to_devnull()
            sys.exit(1)

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
                "Will now wait for %s because of following exception:" % pretty_time,
                exc_name,
                "Exception message: %s" % exc_msg,
                "",
            ]

        else:
            msg = [record.msg, ""]

        console.log_with_time("\n".join(msg), style="warning")


def acquire_cross_platform_stdout():

    # As per #254: stdout need to be wrapped so that windows get a correct csv
    # stream output
    if "windows" in platform.system().lower():
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


def create_fetch_like_report_iterator(
    cli_args: SimpleNamespace, reader: casanova.Reader
) -> Iterator[FetchReportLikeItem]:

    headers = reader.headers
    input_dir = cli_args.input_dir or ""

    # TODO: deal with no_headers
    assert headers is not None

    filename_pos = headers.get(cli_args.column) if cli_args.column is not None else None
    error_pos = headers.get(cli_args.error_column)
    status_pos = headers.get(cli_args.status_column)
    encoding_pos = headers.get(cli_args.encoding_column)
    mimetype_pos = headers.get(cli_args.mimetype_column)
    body_pos = headers.get(cli_args.body_column)

    for i, row in reader.enumerate():
        item = FetchReportLikeItem(index=i, row=row)

        if error_pos is not None:
            error = get(row, error_pos, "").strip()

            if error:
                item.error = "errored"
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

        if filename_pos is not None:
            filename = get(row, filename_pos, "").strip()

            if filename:
                item.path = join(input_dir, filename)

        if body_pos is not None:
            body = get(row, body_pos)

            if body is not None:
                item.text = body

        if item.path is None and item.text is None:
            item.error = "no-filename-nor-body"
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
                total=total, stats=stats, **loading_bar_kwargs
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
    multiplex=None,
    show_label: bool = False,
):
    def decorate(action):
        @wraps(action)
        def wrapper(cli_args, *args, **kwargs):
            enricher_context = nullcontext()

            completed = 0

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
                    title="Reading output to resume", unit="lines", transient=True
                )
                enricher_context = resume_loading_bar

                def listener(event, _):
                    nonlocal completed

                    if event == "output.row.read":
                        resume_loading_bar.advance()
                        completed += 1

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

            with enricher_context:
                enricher = enricher_fn(
                    cli_args.input if not callable(get_input) else get_input(cli_args),
                    cli_args.output,
                    add=headers(cli_args)
                    if callable(headers) and not is_tabular_record_class(headers)
                    else headers,
                    select=cli_args.select,
                    total=getattr(cli_args, "total", None),
                    multiplex=multiplex(cli_args) if callable(multiplex) else multiplex,
                    **enricher_kwargs
                )

            with LoadingBar(
                title=title(cli_args) if callable(title) else title,
                total=enricher.total,
                unit=unit(cli_args) if callable(unit) else unit,
                sub_unit=sub_unit(cli_args) if callable(sub_unit) else sub_unit,
                nested=nested,
                stats=stats,
                stats_sort_key=stats_sort_key,
                show_label=show_label,
                completed=completed,
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
