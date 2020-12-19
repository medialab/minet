import re
import tld
import justext
import tldextract
from glob import iglob
from os.path import dirname, join
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    'encodings.idna'
]

for p in iglob('minet/cli/**/*.py', recursive=True):
    if '__main__' in p:
        continue

    if '__init__' in p:
        p = re.sub(r'/__init__.py$', '.py', p)

    m = p.replace('/', '.')[:-3]

    hiddenimports.append(m)

hiddenimports.extend(collect_submodules('pkg_resources'))

datas = [
    (
        join(dirname(tld.__file__), 'res', 'effective_tld_names.dat.txt'),
        'tld/res'
    ),
    (
        join(dirname(tldextract.__file__), '.tld_set_snapshot'),
        'tldextract'
    )
]

for p in iglob(join(dirname(justext.__file__), 'stoplists', '*.txt')):
    datas.append((p, 'justext/stoplists'))

__all__ = ['datas', 'hiddenimports']
