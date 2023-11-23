from minet.rate_limiting import (
    RateLimitedIterator,
    RateLimiterState,
    RetryableIterator,
    rate_limited,
    rate_limited_method,
    ThreadsafeBurstyRateLimiterState,
)


# def print_title(title):
#     print()
#     print(title)


# print_title("retryable")
# iterator = RetryableIterator(range(3))

# retries = 0
# for i in iterator:
#     print(i, iterator.retries)
#     if i == 1 and retries < 2:
#         retries += 1
#         iterator.retry()
#         continue

# print_title("retryable rate limited")
# iterator = RateLimitedIterator(range(3), 50)

# retries = 0
# for i in iterator:
#     print(i, iterator.retries)
#     if i == 1 and retries < 2:
#         retries += 1
#         iterator.retry()
#         continue

# print_title("empty rate limited")
# for i in RateLimitedIterator(range(0), 1):
#     print(i)

# print_title("rate limited")
# for i in RateLimitedIterator(range(5), 1):
#     print(i)

# print_title("decorator")


# @rate_limited(1)
# def work(i):
#     print(i)


# for i in range(5):
#     work(i)

# print_title("method decorator")


# class Worker(object):
#     def __init__(self):
#         self.state = RateLimiterState(1)

#     @rate_limited_method("state")
#     def work(self, i):
#         print(i)


# worker = Worker()
# for i in range(5):
#     worker.work(i)

import time


class Client:
    def __init__(self):
        self.rate_limiter_state = ThreadsafeBurstyRateLimiterState(2, 5)

    @rate_limited_method()
    def call(self, value):
        print("before call")
        time.sleep(1)
        print("after call")
        return value


client = Client()

from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    for result in executor.map(client.call, range(10)):
        print(result)
