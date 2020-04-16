import time
from minet.utils import RateLimitedIterator

for i in RateLimitedIterator(range(0), 1):
    print(i)

print('start')
for i in RateLimitedIterator(range(5), 1):
    print(i)
