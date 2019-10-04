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

    def __init__(self, file):
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
