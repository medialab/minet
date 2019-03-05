# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
import csv
from collections import namedtuple
from tqdm import tqdm


def custom_reader(f, target_header):

    reader = csv.reader(f)

    headers = next(reader, None)

    if isinstance(target_header, tuple):
        HeaderPositions = namedtuple('HeaderPositions', target_header)
        position = HeaderPositions(**{t: headers.index(t) for t in target_header})
    else:
        position = headers.index(target_header)

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
