# Minet Crawlers

If you need to quickly implement a performant and resilient web crawler with custom logic, `minet.crawl` provides a handful of building blocks that you can easily repurpose to suit your use-case.

As such, `minet` crawlers are multi-threaded, can defer computations to a process pool, can be made persistent to deal with large queues of urls and to be able to resume.

## Summary

- [Examples](#examples)
  - [The most simple crawler](#the-most-simple-crawler)
  - [The most simple crawler, with typings](#the-most-simple-crawler-with-typings)
- [Crawler](#crawler)
- [CrawlTarget](#crawltarget)
- [CrawlJob](#crawljob)
- [CrawlResult](#crawlresult)

## Examples

### The most simple crawler

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
  title = response.soup().scrape('meta > title')

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

### The most simple crawler, with typings

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
  title = response.soup().scrape('meta > title')

  # Extracting links
  urls = response.links()

  # We return some extracted data, then the next urls to enqueue
  return title, urls
```

<!-- TODO: plural spiders, crawl targets, auto join, auto depth, auto spider dispatch -->

## Crawler

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