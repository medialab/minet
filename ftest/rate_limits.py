import time
from minet import RateLimitedIterator, RetryableIterator

iterator = RetryableIterator(range(3))

retries = 0
for i in iterator:
    print(i, iterator.retries)
    if i == 1 and retries < 2:
        retries += 1
        iterator.retry()
        continue

iterator = RateLimitedIterator(range(3), 50)

retries = 0
for i in iterator:
    print(i, iterator.retries)
    if i == 1 and retries < 2:
        retries += 1
        iterator.retry()
        continue

for i in RateLimitedIterator(range(0), 1):
    print(i)

print('start')
for i in RateLimitedIterator(range(5), 1):
    print(i)
