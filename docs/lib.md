# Minet Library Usage

## Summary

Note that if you are interested in the url cleaning, extraction and join methods exposed by minet's CLI, all of the used functions can be found in the [ural](https://github.com/medialab/ural) package instead.

*Generic utilities*

* [Scraper](#scraper)
* [multithreaded_fetch](#multithreaded_fetch)
* [multithreaded_resolve](#multithreaded_resolve)

*Platform-related utilities*

* [CrowdTangle](./crowdtangle.md)
* [Facebook](./facebook.md)
* [Google](./google.md)
* [Mediacloud](./mediacloud.md)
* [Twitter](./twitter.md)

## Scraper

Scraper class taking a scraper definition (as defined [here](../cookbook/scraping_dsl.md)) and able to extract the declared items from any given piece of html.

Note that upon instantiation, a scraper will 1. validate its definition and raise an error if invalid and 2. perform analysis of its definition to extract some information about it.

```python
from minet import Scraper

scraper_definition = {
  'iterator': 'p'
}

scraper = Scraper(scraper_definition)

# Using your scraper on some html
data = scraper(some_html)

# You can also create a scraper from a JSON or YML file
scraper = Scraper('./scraper.yml')

with open('./scraper.json') as f:
  scraper = Scraper(f)
```

*Arguments*

* **definition** *dict*: scraper definition written using minet's DSL.
* **strain** *?str*: optional CSS selector to be used to build a [`bs4.SoupStrainer`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#parsing-only-part-of-a-document) that will be used on any html to filter out some unnecessary parts as an optimization mechanism.

*Attributes*

* **definition** *dict*: definition used by the scraper.
* **headers** *list*: CSV headers if they could be statically inferred from the scraper's definition.
* **plural** *bool*: whether the scraper was analyzed to yield single items or a list of items.
* **output_type** *str*: the kind of data the scraper will output. Can be `scalar`, `dict`, `list`, `collection` or `unknown`.

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
* **domain_parallelism** *?int* [`1`]: Max number of urls per domain to hit at the same time.
* **buffer_size** *?int* [`25`]: Max number of items per domain to enqueue into memory in hope of finding a new domain that can be processed immediately.
* **insecure** *?bool* [`False`]: Whether to ignore SSL certification errors when performing requests.
* **timeout** *?float|urllib3.Timeout*: Custom timeout for every request.

*Yields*:

A `FetchResult` having the following attributes:

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
* **follow_js_relocation** *?bool* [`False`]: Whether to follow typical JavaScript window relocation. It's more costly because we need to stream the start of the response's body and cannot rely on headers alone.
* **infer_redirection** *?bool* [`False`]: Whether to heuristically infer redirections from urls by using `ural.infer_redirection`?
* **canonicalize** *?bool* [`False`]: Whether to try to find the canonical url from the html source code of the web page. It's more costly because we need to stream the start of the response's body.
* **buffer_size** *?int* [`25`]: Max number of items per domain to enqueue into memory in hope of finding a new domain that can be processed immediately.
* **insecure** *?bool* [`False`]: Whether to ignore SSL certification errors when performing requests.
* **timeout** *?float|urllib3.Timeout*: Custom timeout for every request.

*Yields*:

A `ResolveResult` having the following attributes:

* **url** *?string*: the fetched url.
* **item** *any*: original item from the iterator.
* **error** *?Exception*: an error.
* **stack** *?list*: the redirection stack.
