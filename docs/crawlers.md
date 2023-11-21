# Minet Crawlers

If you need to quickly implement a performant and resilient web crawler with custom logic, `minet.crawl` provides a handful of building blocks that you can easily repurpose to suit your use-case.

As such, `minet` crawlers are multi-threaded, can defer computations to a process pool, can be made persistent to deal with large queues of urls and to be able to resume.

## Summary

- [Examples](#examples)
  - [The simplest crawler](#the-simplest-crawler)
  - [The simplest crawler, with typings](#the-simplest-crawler-with-typings)
  - [Using multiple spiders](#using-multiple-spiders)
  - [Implementing a more complex spider](#implementing-a-more-complex-spider)
- [Crawler](#crawler)
  - [\_\_len\_\_](#__len__)
  - [\_\_iter\_\_](#__iter__)
  - [crawl](#crawl)
  - [enqueue](#enqueue)
  - [start](#start)
  - [stop](#stop)
  - [write](#write)
  - [submit](#submit)
- [Spider](#spider)
  - [Implementable class properties](#implementable-class-properties)
    - [START_URL](#start_url)
    - [START_URLS](#start_urls)
    - [START_TARGET](#start_target)
    - [START_TARGETS](#start_targets)
  - [Implementable methods](#implementable-methods)
    - [start](#start-1)
    - [process](#process)
  - [Methods](#methods-1)
    - [write](#write-1)
    - [submit](#submit-1)
- [CrawlTarget](#crawltarget)
- [CrawlJob](#crawljob)
- [CrawlResult](#crawlresult)

## Examples

### The simplest crawler

In `minet`, a crawler is a multithreaded executor that reads from a queue of jobs (the combination of a url to request alongside some additional data & parameters) and perform HTTP requests for you.

Then, a crawler needs to be given one or several "spiders" that will process the result of a given crawl job (typically exposing a completed HTTP response) to extract some data and potentially enqueue the next jobs to perform.

The most simple "spider" is therefore a function taking a [crawl job](#crawljob) and a HTTP [response](./web.md#response) that must return some extracted data and the next urls to enqueue.

Let's create such a spider:

```python
def spider(job, response):

  # We are only interested in extracting stuff from completed HTML responses
  if response.status != 200 or not response.is_html:

    # NOTE: the function can return nothing, which is the same a
    # returning (None, None), meaning no data, no next urls.
    return

  # Scraping the page's title
  title = response.soup().scrape_one("meta > title")

  # Extracting links
  urls = response.links()

  # We return some extracted data, then the next urls to enqueue
  return title, urls
```

Now we can create a [Crawler](#crawler) using our `spider` function and iterate over [crawl results](#crawlresult) downstream:

```python
from minet.crawl import Crawler

# Always prefer using the context manager that ensures the resources
# managed by the crawler will be correctly cleaned up:
with Crawler(spider) as crawler:

  # Enqueuing our start url:
  crawler.enqueue("https://www.lemonde.fr")

  # Iterating over the crawler's results (after spider processing)
  for result in crawler:
    print("Url", result.url)

    if result.error is not None:
      print("Error", result.error)
    else:
      print("Depth", result.depth)
      print("Title", result.data)
```

### The simplest crawler, with typings

If you want to rely on python [typings](https://docs.python.org/3/library/typing.html) when writing your spider, know that `minet.crawl` APIs are all completely typed.

Here is how one would write a typed spider function:

```python
from minet.web import Response
from minet.crawl import CrawlJob, SpiderResult

def spider(job: CrawlJob, response: Response) -> SpiderResult[str]:

  # We are only interested in extracting stuff from completed HTML responses
  if response.status != 200 or not response.is_html:

    # NOTE: the function can return nothing, which is the same a
    # returning (None, None), meaning no data, no next urls.
    return

  # Scraping the page's title
  title = response.soup().scrape_one('meta > title')

  # Extracting links
  urls = response.links()

  # We return some extracted data, then the next urls to enqueue
  return title, urls
```

And when using the crawler:

```python
from minet.crawl import Crawler, ErroredCrawlResult

# Always prefer using the context manager that ensures the resources
# managed by the crawler will be correctly cleaned up:
with Crawler(spider) as crawler:

  # Enqueuing our start url:
  crawler.enqueue("https://www.lemonde.fr")

  # Iterating over the crawler's results (after spider processing)
  for result in crawler:
    print("Url", result.url)

    if isintance(result, ErroredCrawlResult):
      print("Error", result.error)
      continue

    # NOTE: here result is correctly narrowed to SuccessfulCrawlResult
    print("Depth", result.depth)
    print("Title", result.data)
```

### Using multiple spiders

Sometimes you might want to separate the processing logic into multiple functions/spiders.

For instance, one of the spider might scrape and navigate some pagination, while some other one might be scraping the articles found in said pagination.

In that case, know that a crawler is able to accept multiple spiders given as a dict mapping names to spider function or [Spider](#spider) instances.

```python
from minet.crawl import Crawler, CrawlTarget

def pagination_spider(job, response):
  next_link = response.soup().scrape_one("a.next", "href")

  if next_link is None:
    return

  return None, CrawlTarget(next_link, spider="article")

def article_spider(job, response):
  titles = response.soup().scrape("h2")

  return titles, None

spiders = {
  "pagination": pagination_spider,
  "article": article_spider
}

with Crawler(spiders) as crawler:
  crawler.enqueue("http://someurl.com", spider="pagination")

  for result in crawler:
    print("From spider:", result.spider, 'got result:', result)
```

### Implementing a more complex spider

Sometimes a function might not be enough and you might want to be able to design more complex spiders. Indeed, what if you want to specify custom starting logic, custom request arguments for the calls or use the crawler's utilities wrt the threadsafe file writer or process pool?

For this, you need to implement your own spider, that must inherit from the [Spider](#spider) class.

A spider class MVP needs at least to implement a `process` method that will perform the same job as its function counterpart that we learnt about earlier.

```python
from minet.crawl import Crawler, Spider

class MySpider(Spider):
  def process(self, job, response):
    if response.status != 200 or not response.is_html:
      return

    return None, response.links()

# NOTE: we are now giving an instance of MySpider to the Crawler, not the class itself
# This means you can now use your spider class __init__ to parametrize the spider if
# required.
with Crawler(MySpider()) as crawler:
  for result in crawler:
    ...
```

*Declaring starting targets*

```python
from minet.crawl import Spider, CrawlTarget

# Using any of those class attributes:
class MySpider(Spider):
  START_URL = "http://lemonde.fr"
  START_URLS = ["http://lemonde.fr", "http://lefigaro.fr"],
  START_TARGET = CrawlTarget(url="http://lemonde.fr")
  START_TARGETS = [CrawlTarget(url="http://lemonde.fr"), CrawlTarget(url="http://lefigaro.fr")]

# Implementing the start method
class MySpider(Spider):
  def start():
    yield "http://lemonde.fr"
    yield CrawlTarget(url="http://lefigaro.fr")
```

*Accessing the crawler's utilities*

```python
from minet.crawl import Crawler, Spider

class MySpider(Spider):
  def process(self, job, response):
    if response.status != 200 or not response.is_html:
      return

    # Submitting a computation to the process pool:
    data = self.submit(heavy_computation_function, response.body)

    # Writing a file to disk in a threadsafe manner:
    self.write(data.path, response.body, compress=True)

    return data, response.links()
```

## Crawler

### Arguments

- **spider_or_spiders** *Spider | dict[str, Spider]*: either a single spider (only a processing function or a [Spider](#spider) instance) or a dict mapping a name to processing functions or [Spider](#spider) instances.
- **max_workers** *Optional[int]*: number of threads to be spawned by the pool. Will default to some sensible number based on your number of CPUs.
- **persistent_storage_path** *Optional[str]*: path to a folder that will contain persistent on-disk resources for the crawler's queue and url cache. If not given, the crawler will work entirely in-memory, which means memory could be exceeded if the url queue or cache becomes too large and you also won't be able to resume if your python process crashes.
- **resume** *bool* `False`: whether to attempt to resume from persistent storage. Will raise if `persistent_storage_path=None`.
- **visit_urls_only_once** *bool* `False`: whether to guarantee the crawler won't visit the same url twice.
- **normalized_url_cache** *bool* `False`: whether to use [`ural.normalize_url`](https://github.com/medialab/ural#normalize_url) before adding a url to the crawler's cache. This can be handy to avoid visting a same page having subtly different urls twice. This will do nothing if `visit_urls_only_once=False`.
- **max_depth** *Optional[int]*: global maximum allowed depth for the crawler to accept a job.
- **writer_root_directory** *Optional[str]*: root directory that will be used to resolve path written by the crawler's own threadsafe file writer.
- **sqlar** *bool* `False`: whether the crawler's threadsafe file writer should target a [sqlar](https://www.sqlite.org/sqlar/doc/trunk/README.md) archive instead.
- **lifo** *bool* `False`: whether to process the crawler queue if Last-In, First-Out (LIFO) order. By default the crawler queue is First-In, First-Out (FIFO). Note that this may not hold if you provide a custom `priority` with your jobs. What's more, given the multithreaded nature and complex scheduling of the crawler, the order may not hold locally.
- **domain_parallelism** *int* `1`: maximum number of concurrent calls allowed on a same domain.
- **throttle** *float* `0.2`: time to wait, in seconds, between two calls to the same domain.
- **process_pool_workers** *Optional[int]*: number of processes to spawn that can be used by the crawler and its spiders to delegate CPU-intensive tasks through their `#.submit` method.
- **wait** *bool* `True`: whether to wait for the threads to be joined when terminating the pool.
- **daemonic** *bool* `False`: whether to spawn daemon threads.
- **timeout** *Optional[float | urllib3.Timeout]*: default timeout to be used for any HTTP call.
- **insecure** *bool*: whether to allow insecure HTTPS connections.
- **spoof_tls_ciphers** *bool* `False`: whether to spoof the TLS ciphers.
- **proxy** *Optional[str]*: url to a proxy server to be used.
- **retry** *bool* `False`: whether to allow the HTTP calls to be retried.
- **retryer_kwargs** *Optional[dict]*: arguments that will be given to [create_reques.t_retryer](./web.md#create_request_retryer) to create the retryer for each of the spawned threads.
- **request_args** *Optional[Callable[[T], dict]]*: function returning arguments that will be given to the threaded [request](./web.md#request) call for a given item from the iterable.
- **use_pycurl** *bool* `False`: whether to use [`pycurl`](http://pycurl.io/) instead of [`urllib3`](https://urllib3.readthedocs.io/en/stable/) to perform the request. The `pycurl` library must be installed for this kwarg to work.
- **compressed** *bool* `False`: whether to automatically specifiy the `Accept` header to ask the server to compress the response's body on the wire.
- **known_encoding** *Optional[str]*: encoding of the body of requested urls. Defaults to `None` which means this encoding will be inferred from the body itself.
- **max_redirects** *int* `5`: maximum number of redirections the request will be allowed to follow before raising an error.
- **stateful_redirects** *bool* `False`: whether to allow the resolver to be stateful and store cookies along the redirection chain. This is useful when dealing with GDPR compliance patterns from websites etc. but can hurt performance a little bit.
- **spoof_ua** *bool* `False`: whether to use a plausible `User-Agent` header when performing requests.

### Properties

- **singular** *bool*: `True` if the crawler handles a single spider.
- **plural** *bool*: `True` if the crawler handles multiple spiders.

### Methods

#### \_\_len\_\_

Returns the current length of the queue.

```python
crawler.enqueue("https://www.lemonde.fr")

len(crawler)
>>> 1
```

#### \_\_iter\_\_

Actually starts the crawler's scheduling and iterate over the crawler's results yielded as [CrawlResult](#crawlresult) objects.

Same as calling the [#.crawl](#crawl) method without arguments.

```python
for result in crawler:
  print(result)
```

#### crawl

Actually starts the crawler's scheduling and iterate over the crawler's results yielded as [CrawlResult](#crawlresult) objects.


```python
# Basic usage
for result in crawler.crawl():
  print(result)

# Using a callback
def callback(crawler, result):
  path = result.data.path + ".html"
  crawler.write(path, result.response.body)

  return path

for result, written_path in crawler.crawl(callback=callback):
  print("Response was written to:", written_path)
```

*Arguments*

- **callback** *Optional[Callable[[Crawler, SuccessfulCrawlResult], T]]*: callback that can be used to perform IO-intensive tasks within the same thread used for peforming the crawler's request and to return additional information. If callback is given, the iterator returned by the method will yield `(result, callback_result)` instead of just `result`. Note that this callback must be threadsafe.

#### enqueue

Method used to atomically add a single target to crawl or an iterable of targets to crawl.

Will return the number of jobs actually created an enqueued (if `visit_urls_only_once=True` or `max_depth!=None`, for instance, some targets might be discarded).

Note that, usually, new targets are not enqueued manually to the crawler but rather as an implicit result of some spider's processing or when specifying start targets when implementing a [Spider](#spider).

```python
from minet.crawl import CrawlTarget

# Can take a single url
crawler.enqueue("https://www.lemonde.fr")

# Can take a single crawl target
crawler.enqueue(CrawlTarget(url="https://www.lemonde.fr", priority=5))

# Can take an iterable of urls
crawler.enqueue([
  "https://www.lemonde.fr",
  "https://lefigaro.fr"
])

# Can take an iterable of crawl targets
crawler.enqueue([
  CrawlTarget(url="https://www.lemonde.fr", priority=5)
  CrawlTarget(url="https://lefigaro.fr", priority=6)
])
```

*Arguments*

- **target_or_targets** *str | CrawlTarget | Iterable[str] | Iterable[CrawlTarget]*: targets to enqueue.
- **spider** *Optional[str]*: override target spider.
- **depth** *Optional[int]*: override target depth.
- **base_url** *Optional[str]*: optional base url that will be used to resolve relative targets.
- **parent** *Optional[[CrawlJob](#crawljob)]: override parent job.

#### start

Method used to manually start the crawler and enqueue start jobs if necessary (when not resuming).

This method is automatically called when using the crawler as a context manager.

#### stop

Method used to manually stop the crawler and cleanup the associated resources (the thread pool, the process pool, flush the persistent caches and close the SQLite connections etc.).

This method is automatically called when using the crawler as a context manager.

#### write

Use the crawler's internal threadsafe file writer to write the given binary or text content to disk.

Returns the actually written path after resolution and extension mangling.

*Arguments*

- **filename** *str*: path to write. Will be resolved with the crawler's `writer_root_directory` if relative.
- **contents** *str | bytes*: text content, binary or text, to write to disk.
- **relative** *bool* `False`: if `True`, the returned path will be relative instead of absolute.
- **compress** *bool* `False`: whether to gzip the file when writing. Will add `.gz` to the path if necessary.

#### submit

Submit a function to be run in a process from the pool managed by the crawler. If `process_pool_workers` is less than `1`, the function will run synchronously in the same process as the crawler.

```python
def heavy_html_processing(html: bytes):
  return something_hard_to_compute(html)

result = crawler.submit(heavy_html_processing, some_html)
```

## Spider

### Implementable class properties

#### START_URL

Class property that you can use to specify a single starting url.

#### START_URLS

Class property that you can use to specify multiple starting urls as a non-lazy iterable (implement the [#.start](#start-1) method for lazy iterables, generators etc.).

#### START_TARGET

Class property that you can use to specify a single starting [CrawlTarget](#crawltarget).

#### START_TARGETS

Class property that you can use to specify multiple starting [[CrawlTarget](#crawltarget)] objects as a non-lazy iterable (implement the [#.start](#start-1) method for lazy iterables, generators etc.).

### Implementable methods

#### start

Method that must return an iterable of crawl targets as urls or [CrawlTarget](#crawltarget) instances.

Note that this method is only called the first time the crawler starts, and will not be called again when resuming.

```python
from minet.crawl import Spider

class MySpider(Spider):
  def start():
    yield "http://lemonde.fr"
```

#### process

Method that must be implemented for the spider to be able to process the crawler's completed jobs.

The method takes a [CrawlJob](#crawljob) instance, a HTTP [Response](./web.md#response) and must return either `None` or a 2-tuple containing: 1. some optional & arbitraty data extracted from the response, 2. an iterable of next targets for the crawler to enqueue.

Note that next crawl targets can be relative (they will be resolved wrt current's job last redirected url) and that their depth, if not provided, will default to the current job's depth + 1.

Note also that if the crawler is plural (handling multiple spiders), next target will be dispatched to the same spider by default if a spider name for the target is not provided.

```python
from minet.web import Response
from minet.crawl import Spider, CrawlJob, SpiderResult

class MySpider(Spider):
  def process(self, job: CrawlJob, response: Response) -> SpiderResult:
    if response.status != 200 or not response.is_html:
      return

    return None, response.links()
```

### Methods

#### write

Same as calling the attached crawler's [#.write](#write) method.

#### submit

Same as calling the attached crawler's [#.submit](#submit) method.

## CrawlTarget

A crawl target is an object that will be used by the crawler to spawn new jobs. You can of course directly ask the crawler to enqueue urls directly but using a `CrawlTarget` object enables you to provide more details.

You can for instance specify a custom depth or priority, redirect the job that will be created to other spiders and even pass some useful data along the crawler queue that will be used by spiders to perform their processing.

*Example*

```python
# CrawlTarget with only a url is the same as giving the url directly
target = CrawlTarget("https://www.lemonde.fr")

# Custom priority (lower will be processed first)
target = CrawlTarget("https://www.lemonde.fr", priority=5)

# Delegate to a specific spider for processing and pass some data along
target = CrawlTarget(
  "https://www.lemonde.fr",
  spider="homepage",
  data={"media_type": "national"}
)
```

*Properties*

- **url** *str*: url to request.
- **depth** *Optional[int]*: override depth for the upcoming crawl job.
- **spider** *Optional[str]*: name of target spider for the upcoming crawl job.
- **priority** *int* `0`: custom priority for the upcoming crawl job. Lower means earlier.
- **data** *Optional[T]*: data to pass along.

## CrawlJob

A crawl job is an actual job that was enqueued by the crawler. They are created and managed by the crawler itself and are usually derived from a url or a [CrawlTarget](#crawltarget) object.

Those jobs are also provided to spider's processing functions and can be accessed from a [CrawlResult](#crawlresult) downstream.

*Properties*

- **id** *str*: a unique id referencing the job.
- **url** *str*: the url meant to be requested.
- **group** *str*: the job's group wrt allowed concurrency and throttling. By default, a job's group is the url's domain.
- **depth** *int*: the job's depth.
- **spider** *Optional[str]*: name of the spider tasked to process the job.
- **priority** *int*: the job's priority. Lower means earlier.
- **data** *Optional[T]*: data that was provided by the user along with the job.
- **parent** *Optional[str]*: id of the parent job, if any.

## CrawlResult

*Properties*

- **job** *[CrawlJob](#crawljob)*: job that was completed or errored.
- **data** *Optional[T]*: data extracted by the spider for the job.
- **error** *Optional[Exception]*: error that happend when requesting the job's url.
- **error_code** *Optional[str]*: human-readable error code if an error happened when requesting the job's url.
- **response** *Optional[[Response](./web.md#response)]*: HTTP response if the job did not error.
- **degree** *int*: number of new jobs enqueued when processing this job.
- **url** *str*: shorthand for `result.job.url`.
- **depth** *int*: shorthand for `result.job.depth`.
- **spider** *Optional[str]*: shorthand for `result.job.spider`.

*Typed variants*

```python
from minet.crawl import (
  ErroredCrawlResult,
  SuccessfulCrawlResult
)

errored_result: ErroredCrawlResult
assert errored_result.data is None
assert errored_result.error is not None
assert errored_result.error_code is not None
assert errored_result.response is None

successful_result: SuccessfulCrawlResult
assert successful_result.data is not None
assert successful_result.error is None
assert successful_result.error_code is None
assert successful_result.response is not None
```