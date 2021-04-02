# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
import csv
import sys
import yaml
import platform
from io import StringIO
from glob import iglob
from os.path import join, expanduser, isfile, isdir
from collections import namedtuple
from tqdm import tqdm

from minet.cli.exceptions import MissingColumnError
from minet.utils import fuzzy_int, noop


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

        bar_kwargs = {
            'desc': desc,
            'dynamic_ncols': True,
            'total': total,
            'postfix': stats,
            'unit': unit
        }

        if delay is not None:
            bar_kwargs['delay'] = delay

        self.bar = tqdm(**bar_kwargs)

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
    stdout = sys.stdout

    # As per #254: stdout need to be wrapped so that windows get a correct csv
    # stream output
    if 'windows' in platform.system().lower():
        stdout = open(
            sys.__stdout__.fileno(),
            mode=sys.__stdout__.mode,
            buffering=1,
            encoding=sys.__stdout__.encoding,
            errors=sys.__stdout__.errors,
            newline='',
            closefd=False
        )

    if output is None:
        return DummyTqdmFile(stdout)

    # As per #254: newline='' is necessary for CSV output on windows to avoid
    # outputting extra lines because of a '\r\r\n' end of line...
    return open(output, flag, encoding=encoding, newline='')


WorkerPayload = namedtuple(
    'WorkerPayload',
    ['row', 'headers', 'path', 'encoding', 'content', 'args']
)

REPORT_HEADERS = ['status', 'filename', 'encoding', 'mimetype']


def create_report_iterator(namespace, reader, args=None, on_irrelevant_row=noop):
    for col in REPORT_HEADERS:
        if col not in reader.pos:
            raise MissingColumnError(col)

    status_pos = reader.pos.status
    filename_pos = reader.pos.filename
    encoding_pos = reader.pos.encoding
    mimetype_pos = reader.pos.mimetype
    raw_content_pos = reader.pos.get('raw_contents')

    if raw_content_pos is None and not isdir(namespace.input_dir):
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
