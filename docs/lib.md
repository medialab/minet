# Minet Library Usage

## Summary

Note that if you are interested in the url cleaning, extraction and join methods exposed by minet's CLI, all of the used functions can be found in the [ural](https://github.com/medialab/ural) package instead.

*Generic utilities*

* [scrape](#scrape)
* [Scraper](#scraper)
* [multithreaded_fetch](#multithreaded_fetch)
* [multithreaded_resolve](#multithreaded_resolve)

*Platform-related utilities*

* [CrowdTangle](./crowdtangle.md)
* [Facebook](./facebook.md)
* [Google](./google.md)
* [Mediacloud](./mediacloud.md)
* [Twitter](./twitter.md)

## scrape

Apply a minet scraper definition (described [here](../cookbook/scraping_dsl.md)) to some html or soup and get the extracted data.

```python
from minet import scrape

scraper_definition = {
  'iterator': 'p'
}

data = scrape(scraper_definition, some_html)
```

*Arguments*

* **definition** *dict*: scraper definition written using minet's DSL.
* **html** *str|soup*: either a HTML string or bs4 soup to scrape.
* **engine** *?str* [`lxml`]: bs4 engine to use to parse html.
* **context** *?dict*: optional context to use.

## Scraper

Tiny abstraction built over [#.scrape](#scrape) to "compile" the given definition and apply it easily on multiple html documents.

```python
from minet import Scraper

scraper_definition = {
  'iterator': 'p'
}

scraper = Scraper(scraper_definition)

data = scraper(some_html)

# You can also create a scraper from a JSON or YML file
scraper = Scraper('./scraper.yml')

with open('./scraper.json') as f:
  scraper = Scraper(f)
```

*Arguments*

* **definition** *dict*: scraper definition written using minet's DSL.

*Attributes*

* **definition** *dict*: definition used by the scraper.
* **headers** *list*: CSV headers if they could be statically inferred from the scraper's definition.

## multithreaded_fetch

Function fetching urls in a multithreaded fashion.

```python
from minet import multithreaded_fetch

# Most basic usage
urls = ['https://google.com', 'https://twitter.com']

for result in multithreaded_fetch(urls):
  print(result.url, result.response.status)

# Using a list of dicts

urls = [
  {
    'url': 'https://google.com',
    'label': 'Google'
  },
  {
    'url': 'https://twitter.com',
    'label': 'Twitter'
  }
]

for result in multithreaded_fetch(urls, key=lambda x: x['url']):
  print(result.item['label'], result.response.status)
```

*Arguments*:

* **iterator** *iterable*: An iterator over urls or arbitrary items, if you provide a `key` argument along with it.
* **key** *?callable*: A function extracting the url to fetch from the items yielded by the provided iterator.
* **request_args** *?callable*: A function returning arguments to pass to the internal `request` helper for a call.
* **threads** *?int* [`25`]: Number of threads to use.
* **throttle** *?float|callable* [`0.2`]: Per-domain throttle in seconds. Or a function taking the domain and current item and returning the throttle to apply.
* **max_redirects** *?int* [`5`]: Max number of redirections to follow.
* **guess_extension** *?bool* [`True`]: Whether to attempt to guess the resource's extension.
* **guess_encoding** *?bool* [`True`]: Whether to attempt to guess the resource's encoding.
* **domain_parallelism** *?int* [`1`]: Max number of urls per domain to hit at the same time.
* **buffer_size** *?int* [`25`]: Max number of items per domain to enqueue into memory in hope of finding a new domain that can be processed immediately.
* **insecure** *?bool* [`False`]: Whether to ignore SSL certification errors when performing requests.
* **timeout** *?float|urllib3.Timeout*: Custom timeout for every request.

*Yields*:

A `FetchWorkerResult` having the following attributes:

* **url** *?string*: the fetched url.
* **item** *any*: original item from the iterator.
* **error** *?Exception*: an error.
* **response** *?urllib3.HTTPResponse*: the http response.
* **meta** *?dict*: additional metadata:
  * **mime** *?string*: resource's mimetype.
  * **ext** *?string*: resource's extension.
  * **encoding** *?string*: resource's encoding.


## multithreaded_resolve

Function resolving url redirections in a multithreaded fashion.

```python
from minet import multithreaded_resolve

# Most basic usage
urls = ['https://bit.ly/whatever', 'https://t.co/whatever']

for result in multithreaded_resolve(urls):
  print(result.stack)

# Using a list of dicts

urls = [
  {
    'url': 'https://bit.ly/whatever',
    'label': 'Bit.ly'
  },
  {
    'url': 'https://t.co/whatever',
    'label': 'Twitter'
  }
]

for result in multithreaded_resolve(urls, key=lambda x: x['url']):
  print(result.stack)
```

*Arguments*:

* **iterator** *iterable*: An iterator over urls or arbitrary items, if you provide a `key` argument along with it.
* **key** *?callable*: A function extracting the url to fetch from the items yielded by the provided iterator.
* **resolve_args** *?callable*: A function returning arguments to pass to the internal `resolve` helper for a call.
* **threads** *?int* [`25`]: Number of threads to use.
* **throttle** *?float|callable* [`0.2`]: Per-domain throttle in seconds. Or a function taking the domain and current item and returning the throttle to apply.
* **max_redirects** *?int* [`5`]: Max number of redirections to follow.
* **follow_refresh_header** *?bool* [`False`]: Whether to follow `Refresh` headers or not.
* **follow_meta_refresh** *?bool* [`False`]: Whether to follow meta refresh tags. It's more costly because we need to stream the start of the response's body and cannot rely on headers alone.
* **infer_redirection** *?bool* [`False`]: Whether to heuristically infer redirections from urls by using `ural.infer_redirection`?
* **buffer_size** *?int* [`25`]: Max number of items per domain to enqueue into memory in hope of finding a new domain that can be processed immediately.
* **insecure** *?bool* [`False`]: Whether to ignore SSL certification errors when performing requests.
* **timeout** *?float|urllib3.Timeout*: Custom timeout for every request.

*Yields*:

A `ResolveWorkerResult` having the following attributes:

* **url** *?string*: the fetched url.
* **item** *any*: original item from the iterator.
* **error** *?Exception*: an error.
* **stack** *?list*: the redirection stack.
