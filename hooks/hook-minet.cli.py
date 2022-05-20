import re
import tld
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

datas = [
    (join(dirname(tld.__file__), "res", "effective_tld_names.dat.txt"), "tld/res"),
    (join(dirname(trafilatura.__file__), "settings.cfg"), "trafilatura"),
]

for p in iglob(join(dirname(justext.__file__), "stoplists", "*.txt")):
    datas.append((p, "justext/stoplists"))

__all__ = ["datas", "hiddenimports"]
