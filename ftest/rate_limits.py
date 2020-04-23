import time
from minet import RateLimitedIterator, RetryableIterator, rate_limited

def print_title(title):
    print()
    print(title)

print_title('retryable')
iterator = RetryableIterator(range(3))

retries = 0
for i in iterator:
    print(i, iterator.retries)
    if i == 1 and retries < 2:
        retries += 1
        iterator.retry()
        continue

print_title('retryable rate limited')
iterator = RateLimitedIterator(range(3), 50)

retries = 0
for i in iterator:
    print(i, iterator.retries)
    if i == 1 and retries < 2:
        retries += 1
        iterator.retry()
        continue

print_title('empty rate limited')
for i in RateLimitedIterator(range(0), 1):
    print(i)

print_title('rate limited')
for i in RateLimitedIterator(range(5), 1):
    print(i)

print_title('decorator')

@rate_limited(1)
def work(i):
    print(i)

for i in range(5):
    work(i)
