import tld
from os.path import dirname, join

p = join(dirname(tld.__file__), 'res', 'effective_tld_names.dat.txt')

print(p)
