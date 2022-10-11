# =============================================================================
# Minet Instagram Utils
# =============================================================================
#
# Miscellaneous helper functions used by the minet.instagram namespace.
#

import re
from datetime import datetime


def extract_from_text(text, char):
    splitter = re.compile(r"[^\w%s]+" % char)

    return sorted(
        set(r.lstrip(char).lower() for r in splitter.split(text) if r.startswith(char))
    )


def timestamp_to_isoformat(timestamp):
    return datetime.utcfromtimestamp(timestamp).isoformat()


def short_code_to_url(short_code):
    return "https://www.instagram.com/p/{}/".format(short_code)
