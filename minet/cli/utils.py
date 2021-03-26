# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
import csv
import sys
import gzip
import yaml
import codecs
from io import StringIO
from glob import iglob
from os.path import join, expanduser, isfile, isdir
from collections import namedtuple
from tqdm import tqdm

from minet.cli.exceptions import MissingColumnError


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


def CsvIO(column, value):
    buf = StringIO()
    writer = csv.writer(buf, dialect=csv.unix_dialect, quoting=csv.QUOTE_MINIMAL)
    writer.writerow([column])
    writer.writerow([value])

    buf.seek(0)

    return buf


def edit_namespace_with_csv_io(namespace, column, attr_name='column'):
    namespace.file = CsvIO(column, getattr(namespace, attr_name))
    setattr(namespace, attr_name, column)


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


class LoadingBar(object):
    __slots__ = ('bar', 'stats')

    def __init__(self, desc, total=None, stats=None, unit=None, unit_plural=None,
                 delay=None):
        if unit is not None and total is None:
            if unit_plural is not None:
                unit = ' ' + unit_plural
            else:
                unit = ' ' + unit + 's'

        self.stats = stats or {}

        self.bar = tqdm(
            desc=desc,
            dynamic_ncols=True,
            total=total,
            postfix=stats,
            unit=unit,
            delay=delay
        )

    def update_total(self, total):
        self.bar.total = total

    def set_description(self, desc):
        return self.bar.set_description(desc)

    def update_stats(self, **kwargs):
        for key, value in kwargs.items():
            self.stats[key] = value

        return self.bar.set_postfix(**self.stats)

    def inc(self, name):
        if name not in self.stats:
            self.stats[name] = 0

        self.stats[name] += 1
        return self.update_stats()

    def update(self, n=1):
        return self.bar.update(n)

    def close(self):
        return self.bar.close()

    def print(self, *args, end='\n'):
        msg = ' '.join(str(arg) for arg in args)
        self.bar.write(msg, file=sys.stderr, end=end)

    def die(self, msg):
        self.bar.close()
        die(msg)

    def __enter__(self):
        return self.bar.__enter__()

    def __exit__(self, *args):
        return self.bar.__exit__(*args)


def open_output_file(output, flag='w', encoding='utf-8'):
    if output is None:
        return DummyTqdmFile(sys.stdout)

    return open(output, flag, encoding=encoding)


def read_potentially_gzipped_path(path, encoding='utf-8'):
    if path.endswith('.gz'):
        with open(path, 'rb') as f:
            raw_bytes = gzip.decompress(f.read())

        raw = raw_bytes.decode(encoding, errors='replace')
    else:
        with codecs.open(path, 'r', encoding=encoding, errors='replace') as f:
            raw = f.read()

    return raw


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

    if raw_content_pos is None and not isdir(namespace.input_dir):
        raise NotADirectoryError

    indexed_headers = {h: p for p, h in enumerate(enricher.fieldnames)}

    def generator():
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

            path = join(namespace.input_dir, filename)
            encoding = row[encoding_pos].strip() or 'utf-8'

            yield WorkerPayload(
                row=row,
                headers=indexed_headers,
                path=path,
                encoding=encoding,
                content=None,
                args=args
            )

    return generator()


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
            return yaml.load(f, Loader=yaml.Loader)

    return None
