import re
import tld
import dragnet
from glob import iglob
from os.path import dirname, join

hiddenimports = [
    'lxml',
    'lxml.etree',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree._utils',
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
    ),
    (
        join(dirname(dragnet.__file__), 'pickled_models', 'py3_sklearn_0.18.0', 'kohlschuetter_readability_weninger_content_model.pkl.gz'),
        'dragnet/pickled_models/py3_sklearn_0.18.0'
    )
]

__all__ = ['datas', 'hiddenimports']
