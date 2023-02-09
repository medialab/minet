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
from functools import wraps, partial
from datetime import datetime
from logging import Handler
from tqdm import tqdm
from ebbe import noop, format_seconds

from minet.cli.exceptions import MissingColumnError, FatalError
from minet.utils import fuzzy_int


def with_cli_exceptions(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)

        except BrokenPipeError:

            # Taken from: https://docs.python.org/3/library/signal.html
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)

        except KeyboardInterrupt:
            # Leaving loading bars to avoid duplication
            cleanup_loading_bars()

            # Exiting right now to avoid stack frames
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


def better_and_tqdm_aware_print(*args, file=sys.stdout, sep=" ", end="\n"):
    msg = format_polymorphic_message(*args)
    tqdm.write(msg, file=file, end=end)


print_out = partial(better_and_tqdm_aware_print, file=sys.stdout)
print_err = partial(better_and_tqdm_aware_print, file=sys.stderr)


def die(msg=None):
    if msg is not None:
        if not isinstance(msg, list):
            msg = [msg]

        for m in msg:
            print_err(m)

    sys.exit(1)


def cleanup_loading_bars(leave=False):
    for bar in list(tqdm._instances):
        bar.leave = leave
        bar.close()


def safe_index(l, e):
    try:
        return l.index(e)
    except ValueError:
        return None


class CLIRetryerHandler(Handler):
    def emit(self, record):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if record.source == "request_retryer":
            exc = record.exception
            pretty_time = format_seconds(record.sleep_time)

            exc_name = "%s.%s" % (exc.__class__.__module__, exc.__class__.__name__)
            exc_msg = str(exc)

            msg = [
                "%s" % now,
                "Will now wait for %s because of following exception:" % pretty_time,
                ("%s (%s)" % (exc_name, exc_msg)) if exc_msg else exc_name,
                "",
            ]

        else:
            msg = ["%s" % now, record.msg, ""]

        print_err(msg)


class LoadingBar(tqdm):
    def __init__(
        self, desc, stats=None, unit=None, unit_plural=None, total=None, **kwargs
    ):

        if unit is not None and total is None:
            if unit_plural is not None:
                unit = " " + unit_plural
            else:
                unit = " " + unit + "s"

        self.__stats = stats or {}

        if unit is not None:
            kwargs["unit"] = unit

        super().__init__(desc=desc, total=total, **kwargs)

    def update_total(self, total):
        self.total = total

    def update_stats(self, **kwargs):
        for key, value in kwargs.items():
            self.__stats[key] = value

        return self.set_postfix(**self.__stats)

    def inc(self, name, amount=1):
        if name not in self.__stats:
            self.__stats[name] = 0

        self.__stats[name] += amount
        return self.update_stats()

    def print(self, *args, end="\n"):
        self.write(format_polymorphic_message(*args), file=sys.stderr, end=end)

    def close(self):
        super().close()

    def die(self, msg):
        self.close()
        die(msg)


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


def get_enricher_and_loading_bar(
    cli_args, headers, desc, unit=None, multiplex=None, stats=None
):
    if callable(headers):
        headers = headers(cli_args)

    if callable(multiplex):
        multiplex = multiplex(cli_args)

    enricher = casanova.enricher(
        cli_args.file,
        cli_args.output,
        add=headers,
        keep=cli_args.select,
        total=getattr(cli_args, "total", None),
        multiplex=multiplex,
    )

    loading_bar = LoadingBar(desc=desc, unit=unit, total=enricher.total, stats=stats)

    return enricher, loading_bar


def with_enricher_and_loading_bar(headers, desc, unit=None, multiplex=None, stats=None):
    def decorate(action):
        @wraps(action)
        def wrapper(cli_args, *args, **kwargs):
            enricher, loading_bar = get_enricher_and_loading_bar(
                cli_args,
                headers=headers,
                desc=desc,
                unit=unit,
                multiplex=multiplex,
                stats=stats,
            )

            additional_kwargs = {"enricher": enricher, "loading_bar": loading_bar}

            return action(cli_args, *args, **additional_kwargs, **kwargs)

        return wrapper

    return decorate
