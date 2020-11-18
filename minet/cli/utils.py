# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
import sys
import yaml
from io import StringIO
from glob import iglob
from os.path import join, expanduser, isfile
from collections import namedtuple
from tqdm import tqdm

from minet.cli.exceptions import MissingColumnError


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def die(msg):
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


def CsvIO(column, value):
    return StringIO('%s\n%s' % (column, value))


def edit_namespace_with_csv_io(namespace, column):
    namespace.file = CsvIO(column, namespace.column)
    namespace.column = column


class DummyTqdmFile(object):
    """
    Dummy file-like that will write to tqdm. Taken straight from the lib's
    documentation: https://github.com/tqdm/tqdm but modified for minet use
    case regarding stdout piping.
    """
    file = None

    def __init__(self, file=sys.stdout):
        self.file = file
        self.cursor = 0

    def write(self, x):
        self.cursor += 1
        # Avoid print() second call (useless \n)
        tqdm.write(x, file=self.file, end='')

    def flush(self):
        return self.file.flush()

    def tell(self):
        return self.cursor

    def close(self):
        pass


def open_output_file(output, flag='w'):
    if output is None:
        return DummyTqdmFile(sys.stdout)

    return open(output, flag)


WorkerPayload = namedtuple(
    'WorkerPayload',
    ['row', 'headers', 'path', 'encoding', 'content', 'args']
)

REPORT_HEADERS = ['status', 'filename', 'encoding']


def create_report_iterator(namespace, enricher, args=None, loading_bar=None):
    for col in REPORT_HEADERS:
        if col not in enricher.pos:
            raise MissingColumnError(col)

    status_pos = enricher.pos.status
    filename_pos = enricher.pos.filename
    encoding_pos = enricher.pos.encoding
    raw_content_pos = enricher.pos.get('raw_contents')

    indexed_headers = {h: p for p, h in enumerate(enricher.fieldnames)}

    for row in enricher:
        status = int(row[status_pos]) if row[status_pos] else None
        filename = row[filename_pos]

        if status is None or status >= 400 or not filename:
            if loading_bar is not None:
                loading_bar.update()
            continue

        if raw_content_pos is not None:
            yield WorkerPayload(
                row=row,
                headers=indexed_headers,
                path=None,
                encoding=row[encoding_pos],
                content=row[raw_content_pos],
                args=args
            )

            continue

        path = join(namespace.input_directory, filename)
        encoding = row[encoding_pos].strip() or 'utf-8'

        yield WorkerPayload(
            row=row,
            headers=indexed_headers,
            path=path,
            encoding=encoding,
            content=None,
            args=args
        )


def create_glob_iterator(namespace, args):
    for p in iglob(namespace.glob, recursive=True):
        yield WorkerPayload(
            row=None,
            headers=None,
            path=p,
            encoding='utf-8',
            content=None,
            args=args
        )


class LazyLineDict(object):
    def __init__(self, headers, line):
        self.headers = headers
        self.line = line

    def __getitem__(self, key):
        return self.line[self.headers[key]]


class LoadingBarContext(object):
    __slots__ = ('loading_bar',)

    def __init__(self, loading_bar):
        self.loading_bar = loading_bar

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.loading_bar.update()


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

        with open(p) as f:
            return yaml.load(f, Loader=yaml.Loader)

    return None
