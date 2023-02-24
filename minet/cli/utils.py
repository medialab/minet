# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
import os
import sys
import stat
import yaml
import platform
import casanova
from glob import iglob
from os.path import join, expanduser, isfile, relpath
from collections import namedtuple
from collections.abc import Mapping
from functools import wraps
from logging import Handler
from contextlib import nullcontext
from ebbe import noop, format_seconds

from minet.cli.console import console
from minet.cli.loading_bar import LoadingBar
from minet.cli.exceptions import MissingColumnError, FatalError
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


WorkerPayload = namedtuple(
    "WorkerPayload", ["row", "headers", "path", "encoding", "content", "args"]
)


def getdefault(row, pos, default=None):
    if pos is None:
        return default

    try:
        return row[pos] or default
    except IndexError:
        return default


def create_report_iterator(cli_args, reader, worker_args=None, on_irrelevant_row=noop):
    if "filename" not in reader.headers:
        raise MissingColumnError

    filename_pos = reader.headers.filename
    error_pos = reader.headers.get("error")
    status_pos = reader.headers.get("status")
    filename_pos = reader.headers.get("filename")
    encoding_pos = reader.headers.get("encoding")
    mimetype_pos = reader.headers.get("mimetype")
    raw_content_pos = reader.headers.get("raw_contents")

    indexed_headers = {n: i for i, n in enumerate(reader.headers)}

    def generator():
        for i, row in reader.enumerate():
            error = getdefault(row, error_pos)

            if error is not None:
                on_irrelevant_row("errored", row, i)
                continue

            status = fuzzy_int(getdefault(row, status_pos, "200"))

            mimetype = getdefault(row, mimetype_pos, "text/html").strip()
            filename = row[filename_pos]
            encoding = getdefault(row, encoding_pos, "utf-8").strip()

            if status != 200:
                on_irrelevant_row("invalid-status", row, i)
                continue

            if not filename:
                on_irrelevant_row("no-filename", row, i)
                continue

            if "/htm" not in mimetype:
                on_irrelevant_row("invalid-mimetype", row, i)
                continue

            if raw_content_pos is not None:
                yield WorkerPayload(
                    row=row,
                    headers=indexed_headers,
                    path=None,
                    encoding=encoding,
                    content=row[raw_content_pos],
                    args=worker_args,
                )

                continue

            path = join(cli_args.input_dir or "", filename)

            yield WorkerPayload(
                row=row,
                headers=indexed_headers,
                path=path,
                encoding=encoding,
                content=None,
                args=worker_args,
            )

    return generator()


def dummy_csv_file_from_glob(pattern, root_directory=None):
    if root_directory is not None:
        pattern = join(root_directory, pattern)

    yield ["filename"]

    for p in iglob(pattern, recursive=True):
        yield [relpath(p, start=root_directory or "")]


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


def with_loading_bar(**loading_bar_kwargs):
    def decorate(action):
        @wraps(action)
        def wrapper(cli_args, *args, **kwargs):
            total = getattr(cli_args, "total", None)

            with LoadingBar(total=total, **loading_bar_kwargs) as loading_bar:
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
    #
    title=None,
    unit=None,
    sub_unit=None,
    stats=None,
    stats_sort_key=None,
    nested=False,
    multiplex=None,
    show_label=False,
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

            with enricher_context:
                enricher = enricher_fn(
                    cli_args.input if not callable(get_input) else get_input(cli_args),
                    cli_args.output,
                    add=headers(cli_args) if callable(headers) else headers,
                    select=cli_args.select,
                    total=getattr(cli_args, "total", None),
                    multiplex=multiplex(cli_args) if callable(multiplex) else multiplex,
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
