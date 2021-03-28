# =============================================================================
# Minet FileSystem Utilities
# =============================================================================
#
# Multiple helper functions related to reading and writing files.
#
import gzip


def read_potentially_gzipped_path(path, encoding='utf-8'):
    if path.endswith('.gz'):
        with open(path, 'rb') as f:
            raw_bytes = gzip.decompress(f.read())

        raw = raw_bytes.decode(encoding, errors='replace')
    else:
        with codecs.open(path, 'r', encoding=encoding, errors='replace') as f:
            raw = f.read()

    return raw
