# =============================================================================
# Minet Instagram Utils
# =============================================================================
#
# Miscellaneous helper functions used by the minet.instagram namespace.
#
import re
import base64

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


def shortcode_to_url(short_code):
    return "https://www.instagram.com/p/{}/".format(short_code)


# From: https://gist.github.com/sclark39/9daf13eea9c0b381667b61e3d2e7bc11
def shortcode_to_id(shortcode: str) -> int:
    code = ("A" * (12 - len(shortcode))) + shortcode
    return int.from_bytes(base64.b64decode(code.encode(), b"-_"), "big")


def id_to_shortcode(pk: int) -> str:
    bytes_str = base64.b64encode(pk.to_bytes(9, "big"), b"-_")
    return bytes_str.decode().replace("A", " ").lstrip().replace(" ", "A")
