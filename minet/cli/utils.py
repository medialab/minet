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
from ebbe import noop, format_seconds

from minet.cli.console import console
from minet.cli.loading_bar import LoadingBar
from minet.cli.exceptions import MissingColumnError, FatalError
from minet.utils import fuzzy_int


def colored(string, color):
    return "[{color}]{string}[/{color}]".format(string=string, color=color)


def with_cli_exceptions(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)

        except KeyboardInterrupt:
            sys.exit(1)

        except BrokenPipeError:

            # Taken from: https://docs.python.org/3/library/signal.html
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
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


def format_polymorphic_message(*args, sep=" "):
    return sep.join(
        str(item)
        if not isinstance(item, list)
        else "\n".join(str(subitem) for subitem in item)
        for item in args
    )


def variadic_print(*args, file=sys.stdout, sep=" ", end="\n"):
    for arg in args:
        if isinstance(arg, list):
            for msg in arg:
                print(msg, end=end, sep=sep, file=file)
        else:
            print(arg, end=end, sep=sep, file=file)


# NOTE: not using partial to avoid dynamic stream remapping
def print_err(*args):
    variadic_print(*args, file=sys.stderr)


def die(*msg):
    print_err(*msg)

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
                ("%s (%s)" % (exc_name, exc_msg)) if exc_msg else exc_name,
                "",
            ]

        else:
            msg = [record.msg, ""]

        console.log("\n".join(msg), style="warning")


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

    indexed_headers = reader.headers.as_dict()

    def generator():
        for i, row in enumerate(reader):
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


def with_enricher_and_loading_bar(
    headers,
    title,
    unit=None,
    multiplex=None,
):
    def decorate(action):
        @wraps(action)
        def wrapper(cli_args, *args, **kwargs):
            enricher = casanova.enricher(
                cli_args.input,
                cli_args.output,
                add=headers(cli_args) if callable(headers) else headers,
                select=cli_args.select,
                total=getattr(cli_args, "total", None),
                multiplex=multiplex(cli_args) if callable(multiplex) else multiplex,
            )

            # NOTE: if we know that stdout is piped somewhere, we don't
            # bother to wrap it either
            # if (
            #     hasattr(cli_args.output, "fileno")
            #     and callable(cli_args.output.fileno)
            #     and cli_args.output.fileno() == sys.__stdout__.fileno()
            #     and sys.__stdout__.isatty()
            # ):
            #     enricher.writer = csv.writer(sys.stdout)

            with LoadingBar(
                title=title,
                total=enricher.total,
                unit=unit(cli_args) if callable(unit) else unit,
            ) as loading_bar:

                additional_kwargs = {
                    "enricher": enricher,
                    "loading_bar": loading_bar,
                }

                return action(cli_args, *args, **additional_kwargs, **kwargs)

        return wrapper

    return decorate
