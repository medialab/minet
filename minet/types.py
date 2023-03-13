import sys
from typing import Union
from os import PathLike
from io import FileIO
from bs4 import BeautifulSoup

# NOTE: yes this is repetitive, but mypy only understands this, don't ask questions...
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

if sys.version_info >= (3, 11):
    from typing import TypedDict, Required, NotRequired
else:
    from typing_extensions import TypedDict, Required, NotRequired

AnyPath = Union[str, PathLike]
AnyFileTarget = Union[AnyPath, FileIO]
AnyScrapableTarget = Union[str, BeautifulSoup]
