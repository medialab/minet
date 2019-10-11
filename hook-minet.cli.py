import re
import tld
from glob import iglob
from os.path import dirname, join

hiddenimports = [
    'lxml',
    'lxml.etree',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree._utils',
    'sklearn.utils.sparsetools._graph_validation',
    'sklearn.utils.sparsetools._graph_tools',
    'scipy.ndimage',
    'dragnet'
]

for p in iglob('minet/cli/**/*.py', recursive=True):
    if '__main__' in p:
        continue

    if '__init__' in p:
        p = re.sub(r'/__init__.py$', '.py', p)

    m = p.replace('/', '.')[:-3]

    hiddenimports.append(m)

datas = [
    (
        join(dirname(tld.__file__), 'res', 'effective_tld_names.dat.txt'),
        'tld/res'
    )
]

__all__ = ['datas', 'hiddenimports']
