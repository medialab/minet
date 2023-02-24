from typing import Union
from os import PathLike
from io import FileIO

AnyPath = Union[str, PathLike]
AnyFileTarget = Union[AnyPath, FileIO]
