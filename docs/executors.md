# Minet Thread Pool Executors

If you need to download or resolve large numbers of urls as fast as possible and in a multithreaded fashion, the `minet.executors` module provides handy specialized thread pool executors.

Note that those executors are tailored to avoid hitting the same domains too quickly and can be made to respect some throttle time in between calls to the same domain. They were also designed to process lazy streams of urls and to remain very memory-efficient.

They internally leverage the [quenouille](https://github.com/medialab/quenouille) python library to perform their magic.

## Summary

- [HTTPThreadPoolExecutor](#httpthreadpoolexecutor)
- [RequestResult](#requestresult)
- [ResolveResult](#resolveresult)

## HTTPThreadPoolExecutor

*Examples*

```python
from minet.executors import HTTPThreadPoolExecutor

# Always prefer using the context manager that ensures the threadpool
# will be terminated correctly if whatever error happens.
with HTTPThreadPoolExecutor() as executor:

  # Downloading an iterable of urls
  # -------------------------------
  for result in executor.request(urls):

    # NOTE: result is an object representing the result of one job
    # given to the executor by the request method per url.
    print(result)
    print("Url:", result.url)

    if result.error is not None:
      print("Error:", result.error)
    else:
      print("Response:", result.response)

  # Resolving an iterable of urls
  # -----------------------------
  for result in executor.resolve(urls):
    pass

  # Arbitrary iterable (key must return an url for each item)
  # ---------------------------------------------------------
  for result in executor.request(items, key: lambda item: item["url"]):
    print("Item:" result.item)
    print("Url:", result.url)
    pass

  # Using typed variants (when using typings)
  # -----------------------------------------
  from minet.executors import SuccessfulRequestResult, ErroredRequestResult

  for result in executor.request(urls):
    if isinstance(result, ErroredRequestResult):
      print("Error:", result.error)
      continue

    # NOTE: here result is correctly narrowed to SuccessfulRequestResult
    print("Response:", result.response)

  # Using a threaded callback
  # -------------------------
  def callback(item, url, response):
    path = item.path + ".html"

    with open(path, "w") as f:
      f.write(response.body)

    return path

  for result, written_path in executor.request(items, key=..., callback=callback):
    print("Response was written to:", written_path)

  # Shunting domain-wise precautions
  # --------------------------------
  for result in executor.request(urls, domain_parallelism=4, throttle=0):
    pass
```

### Arguments

- **max_workers** *Optional[int]*: number of threads to be spawned by the pool. Will default to some sensible number based on your number of CPUs.
- **wait** *bool* `True`: whether to wait for the threads to be joined when terminating the pool.
- **daemonic** *bool* `False`: whether to spawn daemon threads.
- **timeout** *Optional[float | urllib3.Timeout]*: default timeout to be used for any HTTP call.
- **insecure** *bool*: whether to allow insecure HTTPS connections.
- **spoof_tls_ciphers** *bool* `False`: whether to spoof the TLS ciphers.
- **proxy** *Optional[str]*: url to a proxy server to be used.
- **retry** *bool* `False`: whether to allow the HTTP calls to be retried.
- **retryer_kwargs** *Optional[dict]*: arguments that will be given to [create_request_retryer](./web.md#create_request_retryer) to create the retryer for each of the spawned threads.

### Methods

#### request

Download urls as fast as possible. Yields [RequestResult](#requestresult) objects.

*Arguments*

- **urls** *Iterable[str | T]*: either an iterable of urls or an arbitrary iterable, in which case you must give a `key` returning an url for each item in the iterable.
- **key** *Callable[[T], Optional[str]]*: function returning a url for each item in the given iterable.
- **ordered** *bool* `False`: force the order of the output to be the same as the input, at the cost of performance and increased memory usage.
- **passthrough** *bool* `False`: whether to allow items having no url to "pass through" instead of raising an error.
- **callback** *Optional[Callable[[T, str, Response], C]]*: callback that can be used to perform IO-intensive tasks within the same thread used for the request and to return additional information. If callback is given, the iterator returned by the pool will yield `(result, callback_result)` instead of just `result`. Note that this callback must be threadsafe.
- **request_args** *Optional[Callable[[T], dict]]*: function returning arguments that will be given to the threaded [request](./web.md#request) call for a given item from the iterable.
- **use_pycurl** *bool* `False`: whether to use [`pycurl`](http://pycurl.io/) instead of [`urllib3`](https://urllib3.readthedocs.io/en/stable/) to perform the request. The `pycurl` library must be installed for this kwarg to work.
- **compressed** *bool* `False`: whether to automatically specifiy the `Accept` header to ask the server to compress the response's body on the wire.
- **throttle** *float* `0.2`: time to wait, in seconds, between two calls to the same domain.
- **buffer_size** *int* `1024`: number of items to pull ahead of time from the iterable in hope of finding some url that can be requested immediately. Decreasing this number will ease up memory usage but can slow down overall performance.
- **domain_parallelism** *int* `1`: maximum number of concurrent calls allowed on a same domain.
- **max_redirects** *int* `5`: maximum number of redirections the request will be allowed to follow before raising an error.
- **known_encoding** *Optional[str]*: encoding of the body of requested urls. Defaults to `None` which means this encoding will be inferred from the body itself.

#### resolve

Resolve urls as fast as possible. Yields [ResolveResult](#resolveresult) objects.

*Arguments*

- **urls** *Iterable[str | T]*: either an iterable of urls or an arbitrary iterable, in which case you must give a `key` returning an url for each item in the iterable.
- **key** *Callable[[T], Optional[str]]*: function returning a url for each item in the given iterable.
- **ordered** *bool* `False`: force the order of the output to be the same as the input, at the cost of performance and increased memory usage.
- **passthrough** *bool* `False`: whether to allow items having no url to "pass through" instead of raising an error.
- **callback** *Optional[Callable[[T, str, Response], C]]*: callback that can be used to perform IO-intensive tasks within the same thread used for the request and to return additional information. If callback is given, the iterator returned by the pool will yield `(result, callback_result)` instead of just `result`. Note that this callback must be threadsafe.
- **resolve_args** *Optional[Callable[[T], dict]]*: function returning arguments that will be given to the threaded [resolve](./web.md#resolve) call for a given item from the iterable.
- **use_pycurl** *bool* `False`: whether to use [`pycurl`](http://pycurl.io/) instead of [`urllib3`](https://urllib3.readthedocs.io/en/stable/) to perform the request. The `pycurl` library must be installed for this kwarg to work.
- **compressed** *bool* `False`: whether to automatically specifiy the `Accept` header to ask the server to compress the response's body on the wire.
- **throttle** *float* `0.2`: time to wait, in seconds, between two calls to the same domain.
- **buffer_size** *int* `1024`: number of items to pull ahead of time from the iterable in hope of finding some url that can be requested immediately. Decreasing this number will ease up memory usage but can slow down overall performance.
- **domain_parallelism** *int* `1`: maximum number of concurrent calls allowed on a same domain.
- **max_redirects** *int* `5`: maximum number of redirections the request will be allowed to follow before raising an error.
- **follow_refresh_header** *bool* `True`: whether to allow the request to follow non-standard `Refresh` header redirections.
- **follow_meta_refresh** *bool* `False`: whether to allow the request to sniff the response body to find a `<meta>` tag containing non-standard redirection information.
- **follow_js_relocation** *bool* `False`: whether to allow the request to sniff the response body to find typical patterns of JavaScript url relocation.
- **infer_redirection** *bool* `False`: whether to use [`ural.infer_redirection`](https://github.com/medialab/ural#infer_redirection) to allow redirection inference directly from analyzing the traversed urls.
- **canonicalize** *bool* `False`: whether to allow the request to sniff the response body to find a different canonical url in the a relevant `<link>` tag and push it as a virtual redirection in the stack.


## RequestResult

*Properties*

- **item** *str | T*: item from the iterable given to [request](#request).
- **url** *Optional[str]*: url for the wrapped item, if any.
- **error** *Optional[Exception]*: any error that was raised when peforming the HTTP request.
- **error_code** *Optional[str]*: human-readable error code if any error was raised when performing the HTTP request.
- **response** *Optional[[Response](./web.md#response)]*: the completed response, if no error was raised.

*Typed variants*

```python
from minet.executors import (
  PassthroughRequestResult,
  ErroredRequestResult,
  SuccessfulRequestResult
)

passthrough_result: PassthroughRequestResult
assert passthrough_result.url is None
assert passthrough_result.error is None
assert passthrough_result.error_code is None
assert passthrough_result.response is None

errored_result: ErroredRequestResult
assert errored_result.url is not None
assert errored_result.error is not None
assert errored_result.error_code is not None
assert errored_result.response is None

successful_result: SuccessfulRequestResult
assert successful_result.url is not None
assert successful_result.error is None
assert successful_result.error_code is None
assert successful_result.response is not None
```

## ResolveResult

*Properties*

- **item** *str | T*: item from the iterable given to [resolve](#resolve).
- **url** *Optional[str]*: url for the wrapped item, if any.
- **error** *Optional[Exception]*: any error that was raised when peforming the HTTP request.
- **error_code** *Optional[str]*: human-readable error code if any error was raised when performing the HTTP request.
- **stack** *Optional[List[[Redirection](./web.md#redirection)]]*: the redirection stack if no error was raised.

*Typed variants*

```python
from minet.executors import (
  PassthroughRequestResult,
  ErroredRequestResult,
  SuccessfulRequestResult
)

passthrough_result: PassthroughResolveResult
assert passthrough_result.url is None
assert passthrough_result.error is None
assert passthrough_result.error_code is None
assert passthrough_result.stack is None

errored_result: ErroredResolveResult
assert errored_result.url is not None
assert errored_result.error is not None
assert errored_result.error_code is not None
assert errored_result.stack is None

successful_result: SuccessfulResolveResult
assert successful_result.url is not None
assert successful_result.error is None
assert successful_result.error_code is None
assert successful_result.stack is not None
```
