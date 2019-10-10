# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
import csv
import sys
import json
import argparse
from glob import iglob
from os.path import join
from collections import namedtuple
from tqdm import tqdm


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


def custom_reader(f, target_header):

    reader = csv.reader(f)

    headers = next(reader, None)

    if isinstance(target_header, tuple):
        HeaderPositions = namedtuple('HeaderPositions', target_header)
        position = HeaderPositions(**{t: safe_index(headers, t) for t in target_header})
    else:
        position = safe_index(headers, target_header)

    return headers, position, reader


class DummyTqdmFile(object):
    """
    Dummy file-like that will write to tqdm. Taken straight from the lib's
    documentation: https://github.com/tqdm/tqdm but modified for minet use
    case regarding stdout piping.
    """
    file = None

    def __init__(self, file=sys.stdout):
        self.file = file

    def write(self, x):
        # Avoid print() second call (useless \n)
        tqdm.write(x, file=self.file, end='')

    def flush(self):
        return self.file.flush()

    def close(self):
        pass


class BooleanAction(argparse.Action):
    """
    Custom argparse action to handle --no-* flags.
    Taken from: https://thisdataguy.com/2017/07/03/no-options-with-argparse-and-python/
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(BooleanAction, self).__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, False if option_string.startswith('--no') else True)


class JSONLWriter(object):
    def __init__(self, file):
        self.file = file

    def writerow(self, item):
        row = json.dumps(item, ensure_ascii=False)
        self.file.write(row + '\n')


WorkerPayload = namedtuple(
    'WorkerPayload',
    ['line', 'path', 'encoding', 'content', 'args']
)


def create_report_iterator(namespace, args=None, loading_bar=None):
    input_headers, pos, reader = custom_reader(namespace.report, ('status', 'filename', 'encoding', 'raw_content'))

    for line in reader:
        status = int(line[pos.status]) if line[pos.status] else None
        filename = line[pos.filename]

        if status is None or status >= 400 or not filename:
            if loading_bar is not None:
                loading_bar.update()
            continue

        if pos.raw_content is not None:
            yield WorkerPayload(
                line=line,
                path=None,
                encoding=None,
                content=line[pos.raw_content],
                args=args
            )

            continue

        path = join(namespace.input_directory, filename)
        encoding = line[pos.encoding].strip() or 'utf-8'

        yield WorkerPayload(
            line=line,
            path=path,
            encoding=encoding,
            content=None,
            args=args
        )


def create_glob_iterator(namespace, args):
    for p in iglob(namespace.glob, recursive=True):
        yield WorkerPayload(
            line=None,
            path=p,
            encoding='utf-8',
            content=None,
            args=args
        )
