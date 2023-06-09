# =============================================================================
# Minet Utils
# =============================================================================
#
# Miscellaneous helper function used throughout the library.
#
import re
import hashlib
import json
import time
import string
import importlib
from random import uniform


def fuzzy_int(value):
    try:
        return int(value)
    except ValueError:
        return int(float(value))


def md5(string):
    h = hashlib.md5()
    h.update(string.encode())
    return h.hexdigest()


DOUBLE_QUOTES_RE = re.compile(r'"')


def fix_ensure_ascii_json_string(s):
    try:
        return json.loads('"%s"' % DOUBLE_QUOTES_RE.sub('\\"', s))
    except json.decoder.JSONDecodeError:
        return s


class PseudoFStringFormatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        result = eval(field_name, None, kwargs)

        return result, None


def sleep_with_entropy(seconds, max_random_addendum):
    random_addendum = uniform(0, max_random_addendum)
    time.sleep(seconds + random_addendum)


def is_binary_mimetype(m: str) -> bool:
    if m.startswith("text/"):
        return False

    if not m.startswith("application/"):
        return True

    second_part = m.split("/", 1)[-1]

    return not (
        "json" in second_part
        or "html" in second_part
        or "xml" in second_part
        or "yaml" in second_part
        or "yml" in second_part
        or second_part == "x-httpd-php"
    )


NUMBER_RE = re.compile(r"\d+[\.,]?\d*[KM]?")


def clean_human_readable_numbers(text):
    match = NUMBER_RE.search(text)

    if match is None:
        return text

    approx_likes = match.group(0)

    if "K" in approx_likes:
        approx_likes = str(int(float(approx_likes[:-1]) * 10**3))

    elif "M" in approx_likes:
        approx_likes = str(int(float(approx_likes[:-1]) * 10**6))

    approx_likes = approx_likes.replace(",", "")
    approx_likes = approx_likes.replace(".", "")

    return approx_likes


def message_flatmap(*messages, sep=" ", end="\n"):
    return sep.join(
        end.join(m for m in message) if not isinstance(message, str) else message
        for message in messages
    )


def parse_module_and_target(path, default: str = "main"):
    if ":" in path:
        s = path.rsplit(":", 1)
        return s[0], s[1]

    return path, default


def import_target(path, default: str = "main"):
    module_name, function_name = parse_module_and_target(path, default=default)
    m = importlib.import_module(module_name)

    try:
        return getattr(m, function_name)
    except AttributeError:
        raise ImportError
