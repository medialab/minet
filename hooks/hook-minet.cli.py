from typing import List, Tuple

import re
import playwright_stealth
import trafilatura
import justext
from glob import iglob
from os.path import dirname, join
from PyInstaller.utils.hooks import collect_submodules

SLASH_RE = re.compile(r"[\/\\]")

hiddenimports = []

for p in iglob("minet/cli/**/*.py", recursive=True):
    if "__main__" in p:
        continue

    if "__init__" in p:
        p = re.sub(r"/__init__.py$", ".py", p)

    m = SLASH_RE.sub(".", p)[:-3]

    hiddenimports.append(m)

hiddenimports.extend(collect_submodules("pkg_resources"))
hiddenimports.append("charset_normalizer.md__mypyc")

datas: List[Tuple[str, str]] = [
    (join(dirname(trafilatura.__file__), "settings.cfg"), "trafilatura"),
]

# NOTE: I don't think we need DTD files for our purpose
# for p in iglob(join(dirname(trafilatura.__file__), "data", "*.dtd")):
#     datas.append((p, "trafilatura/data"))

for p in iglob(join(dirname(playwright_stealth.__file__), "js", "*.js")):
    datas.append((p, "playwright_stealth/js"))

for p in iglob(join(dirname(justext.__file__), "stoplists", "*.txt")):
    datas.append((p, "justext/stoplists"))

__all__ = ["datas", "hiddenimports"]
