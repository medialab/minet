import sys
from typing import Union
from os import PathLike
from io import FileIO

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

AnyPath = Union[str, PathLike]
AnyFileTarget = Union[AnyPath, FileIO]
