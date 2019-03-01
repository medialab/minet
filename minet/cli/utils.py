# =============================================================================
# Minet CLI Utils
# =============================================================================
#
# Miscellaneous helpers used by the CLI tools.
#
import csv
from collections import namedtuple


def custom_reader(f, target_header):

    reader = csv.reader(f)

    headers = next(reader, None)

    if isinstance(target_header, tuple):
        HeaderPositions = namedtuple('HeaderPositions', target_header)
        position = HeaderPositions(**{t: headers.index(t) for t in target_header})
    else:
        position = headers.index(target_header)

    return headers, position, reader
