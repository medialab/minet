# =============================================================================
# Minet Instagram Utils
# =============================================================================
#
# Miscellaneous helper functions used by the minet.instagram namespace.
#

import re


def extract_from_text(text, char):
    splitter = re.compile(r"[^\w%s]+" % char)

    return sorted(
        set(r.lstrip(char).lower() for r in splitter.split(text) if r.startswith(char))
    )
