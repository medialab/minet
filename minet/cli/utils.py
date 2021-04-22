# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
import sys
import yaml
import platform
from glob import iglob
from os.path import join, expanduser, isfile, isdir
from collections import namedtuple
from tqdm import tqdm
from ebbe import noop

from minet.cli.exceptions import MissingColumnError
from minet.utils import fuzzy_int


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def die(msg=None):
    if msg is not None:
        if not isinstance(msg, list):
            msg = [msg]

        for m in msg:
            print_err(m)

    sys.exit(1)


def safe_index(l, e):
    try:
        return l.index(e)
    except ValueError:
        return None


class LoadingBar(tqdm):
    def __init__(self, desc, stats=None, unit=None, unit_plural=None,
                 total=None, **kwargs):

        if unit is not None and total is None:
            if unit_plural is not None:
                unit = ' ' + unit_plural
            else:
                unit = ' ' + unit + 's'

        self.__stats = stats or {}

        if unit is not None:
            kwargs['unit'] = unit

        super().__init__(desc=desc, total=total, **kwargs)

    def update_total(self, total):
        self.total = total

    def update_stats(self, **kwargs):
        for key, value in kwargs.items():
            self.__stats[key] = value

        return self.set_postfix(**self.__stats)

    def inc(self, name):
        if name not in self.__stats:
            self.__stats[name] = 0

        self.__stats[name] += 1
        return self.update_stats()

    def print(self, *args, end='\n'):
        msg = ' '.join(str(arg) for arg in args)
        self.write(msg, file=sys.stderr, end=end)

    def die(self, msg):
        self.close()
        die(msg)


def acquire_cross_platform_stdout():

    # As per #254: stdout need to be wrapped so that windows get a correct csv
    # stream output
    if 'windows' in platform.system().lower():
        return open(
            sys.__stdout__.fileno(),
            mode=sys.__stdout__.mode,
            buffering=1,
            encoding=sys.__stdout__.encoding,
            errors=sys.__stdout__.errors,
            newline='',
            closefd=False
        )

    return sys.stdout


WorkerPayload = namedtuple(
    'WorkerPayload',
    ['row', 'headers', 'path', 'encoding', 'content', 'args']
)

REPORT_HEADERS = ['status', 'filename', 'encoding', 'mimetype']


def create_report_iterator(cli_args, reader, worker_args=None, on_irrelevant_row=noop):
    for col in REPORT_HEADERS:
        if col not in reader.pos:
            raise MissingColumnError(col)

    status_pos = reader.pos.status
    filename_pos = reader.pos.filename
    encoding_pos = reader.pos.encoding
    mimetype_pos = reader.pos.mimetype
    raw_content_pos = reader.pos.get('raw_contents')

    if raw_content_pos is None and not isdir(cli_args.input_dir):
        raise NotADirectoryError

    indexed_headers = reader.pos.as_dict()

    def generator():
        for row in reader:
            status = fuzzy_int(row[status_pos]) if row[status_pos] else None
            mimetype = row[mimetype_pos]
            filename = row[filename_pos]

            if status is None:
                on_irrelevant_row('no-status', row)
                continue

            if status != 200:
                on_irrelevant_row('invalid-status', row)
                continue

            if not filename:
                on_irrelevant_row('no-filename', row)
                continue

            if '/htm' not in mimetype:
                on_irrelevant_row('invalid-mimetype', row)
                continue

            if raw_content_pos is not None:
                yield WorkerPayload(
                    row=row,
                    headers=indexed_headers,
                    path=None,
                    encoding=row[encoding_pos],
                    content=row[raw_content_pos],
                    args=worker_args
                )

                continue

            path = join(cli_args.input_dir, filename)
            encoding = row[encoding_pos].strip() or 'utf-8'

            yield WorkerPayload(
                row=row,
                headers=indexed_headers,
                path=path,
                encoding=encoding,
                content=None,
                args=worker_args
            )

    return generator()


def create_glob_iterator(cli_args, worker_args):
    for p in iglob(cli_args.glob, recursive=True):
        yield WorkerPayload(
            row=None,
            headers=None,
            path=p,
            encoding='utf-8',
            content=None,
            args=worker_args
        )


def get_rcfile(rcfile_path=None):
    home = expanduser('~')

    files = [
        rcfile_path,
        '.minetrc',
        '.minetrc.yml',
        '.minetrc.yaml',
        '.minetrc.json',
        join(home, '.minetrc'),
        join(home, '.minetrc.yml'),
        join(home, '.minetrc.yaml'),
        join(home, '.minetrc.json')
    ]

    for p in files:
        if p is None or not isfile(p):
            continue

        with open(p, encoding='utf-8') as f:
            return yaml.safe_load(f)

    return None
