# =============================================================================
# Minet Utils
# =============================================================================
#
# Miscellaneous helper function used throughout the library.
#
from typing import Iterator, Any

import os
import re
import sys
import hashlib
import json
import time
import string
import sqlite3
import importlib
from os.path import dirname, abspath, relpath
from random import uniform

from minet.exceptions import (
    GenericModuleNotFoundError,
    TargetInGenericModuleNotFoundError,
)


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


def import_target(path: str, default: str = "main"):
    module_path_or_name, function_name = parse_module_and_target(path, default=default)

    # NOTE: we normalize to a path, so we can add dir to sys.path
    if not module_path_or_name.endswith(".py"):
        module_path_or_name = module_path_or_name.replace(".", os.sep) + ".py"

    module_path = abspath(module_path_or_name)
    module_directory = dirname(module_path)

    if module_directory not in sys.path:
        sys.path.append(module_directory)

    # NOTE: we renormalize to a module
    module = relpath(module_path)[:-3].replace(os.sep, ".")

    try:
        m = importlib.import_module(module)
    except ImportError:
        raise GenericModuleNotFoundError(module_path_or_name, path)

    sys.path.remove(module_directory)

    try:
        return getattr(m, function_name)
    except AttributeError:
        raise TargetInGenericModuleNotFoundError(
            module_path_or_name, path, function_name
        )


def iterate_over_sqlite_cursor(cursor: sqlite3.Cursor) -> Iterator[Any]:
    while True:
        rows = cursor.fetchmany(128)

        if not rows:
            return

        for row in rows:
            yield row
