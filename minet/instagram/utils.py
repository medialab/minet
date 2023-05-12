# =============================================================================
# Minet Instagram Utils
# =============================================================================
#
# Miscellaneous helper functions used by the minet.instagram namespace.
#

import re

HASHTAGS_RE = re.compile(r"[^\w#]+")
HANDLES_RE = re.compile(r"[^\w\.@]+")


def extract_hashtags(text):
    return sorted(
        set(r.lstrip("#").lower() for r in HASHTAGS_RE.split(text) if r.startswith("#"))
    )


def extract_handles(text):
    return sorted(
        set(r.lstrip("@").lower() for r in HANDLES_RE.split(text) if r.startswith("@"))
    )


def short_code_to_url(short_code):
    return "https://www.instagram.com/p/{}/".format(short_code)
