import sys
from typing import Union, List, Optional
from os import PathLike
from io import FileIO
from bs4 import BeautifulSoup
from urllib3 import Timeout
from ebbe import format_repr

# NOTE: yes this is repetitive, but mypy only understands this, don't ask questions...
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

if sys.version_info >= (3, 10):
    from typing import TypeGuard, Concatenate, ParamSpec
else:
    from typing_extensions import TypeGuard, Concatenate, ParamSpec

if sys.version_info >= (3, 11):
    from typing import TypedDict, Required, NotRequired, Unpack
else:
    from typing_extensions import TypedDict, Required, NotRequired, Unpack

# Useful conditional imports
try:
    from urllib3 import HTTPHeaderDict
except ImportError:
    from urllib3._collections import HTTPHeaderDict

# Useful Any types
AnyPath = Union[str, PathLike]
AnyFileTarget = Union[AnyPath, FileIO]
AnyTimeout = Union[float, Timeout]

# Redirection types
RedirectionType = Literal[
    "hit",
    "location-header",
    "js-relocation",
    "refresh-header",
    "meta-refresh",
    "infer",
    "canonical",
]


class Redirection(object):
    __slots__ = ("status", "type", "url")

    status: Optional[int]
    url: str
    type: RedirectionType

    def __init__(
        self, url: str, _type: RedirectionType = "hit", status: Optional[int] = None
    ):
        self.status = status
        self.url = url
        self.type = _type

    def __repr__(self):
        return format_repr(self, ("type", "status", "url"))


RedirectionStack = List[Redirection]
