# Minet Thread Pool Executors

If you need to download or resolve large numbers of urls as fast as possible and in a multithreaded fashion, the `minet.executors` module provides handy specialized thread pool executors.

Note that those executors are tailored to avoid hitting the same servers too quickly and can be made to respect some throttle time in between calls to the same server. They were also designed to process lazy streams of urls and to remain very memory-efficient.

They internally leverage the [quenouille](https://github.com/medialab/quenouille) python library to perform their magic.

## Summary

- [HTTPThreadPoolExecutor](#httpthreadpoolexecutor)
- [RequestResult](#requestresult)
- [ResolveResult](#resolveresult)

### HTTPThreadPoolExecutor

*Examples*

```python
from minet.executors import HTTPThreadPoolExecutor

# Always prefer using the context manager that ensures the threadpool
# will be terminated correctly if whatever error happens.
with HTTPThreadPoolExecutor() as executor:

  # Downloading an iterable of urls
  for result in executor.request(urls):

    # NOTE: result is an object representing the result of one job
    # given to the executor by the request method per url.
    print(result)
    print('Url:', result.item)

    if result.error is not None:
      print('Error:', result.error)
    else:
      print('Response:', result.response)

  # Resolving an iterable of urls
  for result in executor.resolve(urls):
    pass

  # Custom iterable
  for result in executor.request(items, key: lambda item: item["url"]):
    pass

  # Using typed variants (when using with typings)
  from minet.executors import SuccessfulRequestResult, ErroredRequestResult

  for result in executor.request(urls):
    if isinstance(result, ErroredRequestResult):
      print('Error:', result.error)
      continue

    # NOTE: here result is correctly narrowed to SuccessfulRequestResult
    print('Response:', result.response)
```

#### Arguments

#### Methods

### RequestResult

### ResolveResult
