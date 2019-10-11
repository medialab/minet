import re
from glob import iglob

for p in iglob('minet/cli/**/*.py', recursive=True):
    if '__main__' in p:
        continue

    if '__init__' in p:
        p = re.sub(r'/__init__.py$', '.py', p)

    m = p.replace('/', '.')[:-3]

    print('--hidden-import %s \\' % m)

