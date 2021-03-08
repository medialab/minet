# Minet Library Usage

## Summary

Note that if you are interested in the url cleaning, extraction and join methods exposed by minet's CLI, all of the used functions can be found in the [ural](https://github.com/medialab/ural) package instead.

*Generic utilities*

* [scrape](#scrape)
* [Scraper](#scraper)
* [multithreaded_fetch](#multithreaded_fetch)
* [multithreaded_resolve](#multithreaded_resolve)

*Platform-related commands*

* [CrowdTangleAPIClient](#crowdtangleapiclient)
  * [#.leaderboard](#leaderboard)
  * [#.lists](#lists)
  * [#.post](#crowdtangle-post)
  * [#.posts](#posts)
  * [#.search](#ct-search)
  * [#.summary](#summary)
* [FacebookMobileScraper](#facebookmobilescraper)
  * [#.comments](#facebookmobilescraper-comments)
* [MediacloudClient](#mediacloudclient)
  * [#.count](#count)
  * [#.search](#mc-search)
  * [#.topic_stories](#topic_stories)

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
scraper = Scraper.from_file('./scraper.yml')

with open('./scraper.json') as f:
  scraper = Scraper.from_file(f)
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

## CrowdTangleAPIClient

Client that can be used to access [CrowdTangle](https://www.crowdtangle.com/)'s APIs while ensuring you respect rate limits.

For more details about the CrowdTangle API, be sure to check their [documentation](https://github.com/CrowdTangle/API/wiki).

```python
from minet.crowdtangle import CrowdTangleAPIClient

client = CrowdTangleAPIClient(token='MYTOKEN')

# If you want to use a custom rate limit:
client = CrowdTangleAPIClient(token='MYTOKEN', rate_limit=50)
```

*Arguments*

* **token** *str*: CrowdTangle dashboard API token.
* **rate_limit** *?int* [`6`]: number of allowed hits per minute.

### #.leaderboard

Method yielding stats about the accounts tracked by your dashboard.

```python
for account_stats in client.leaderboard():
  print(account_stats)

# For a specific list:
for account_stats in client.leaderboard(list_id=9457):
  print(account_stats)
```

*Arguments*

* **list_id** *?str*: whether to return only accounts from the given list.
* **limit** *?int*: max number of accounts to return.
* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.
* **partition_strategy** *?str|int*: query partition strategy to use to mitigate the APIs issues regarding pagination. Can be either `day` or a number of results before rolling the query. `500` seems to be a good compromise.
* **per_call** *?bool* [`False`]: whether to yield once per API call or once per retrieved item.

### #.lists

Method returning your dashboard's lists.

```python
lists = client.lists()
```

*Arguments*

* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.

<h3 id="crowdtangle-post">#.post</h3>

Method returning a post's metadata by id.

```python
post = client.post()
```

*Arguments*

* **post_id** *int|str*: id of post to get.
* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.

### #.posts

Method yielding posts from groups or pages tracked by your dashboard.

```python
for post in client.posts():
  print(post)
```

*Arguments*

* **language** *?str*: filter posts by language.
* **list_ids** *?iterable*: retrieve only posts from those lists.
* **sort_by** *?str* [`date`]: how to sort retrieved posts. Can be either `date` or `interaction_date` or `overperforming` or `total_interactions` or `underperforming`.
* **end_date** *?str*: end date.
* **start_date** *?str*: start date.
* **limit** *?int*: max number of posts to return.
* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.
* **partition_strategy** *?str|int*: query partition strategy to use to mitigate the APIs issues regarding pagination. Can be either `day` or a number of results before rolling the query. `500` seems to be a good compromise.
* **per_call** *?bool* [`False`]: whether to yield once per API call or once per retrieved item.

<h3 id="ct-search">#.search</h3>

Method searching for posts based on a given query.

```python
for post in client.search('tree'):
  print(post)
```

*Arguments*

* **terms** *str*: search query.
* **and** *?str*: and component of the query.
* **in_list_ids** *?iterable<str>*: ids of lists in which to search.
* **language** *?str*: filter posts by language.
* **not_in_title** *?bool* [`False`]: whether to search account titles or not.
* **platforms** *?iterable<str>*: only return posts from the given platforms.
* **sort_by** *?str* [`date`]: how to sort retrieved posts. Can be either `date` or `interaction_date` or `overperforming` or `total_interactions` or `underperforming`.
* **end_date** *?str*: end date.
* **start_date** *?str*: start date.
* **types** *?iterable<str>*: only return those post types.
* **limit** *?int*: max number of posts to return.
* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.
* **partition_strategy** *?str|int*: query partition strategy to use to mitigate the APIs issues regarding pagination. Can be either `day` or a number of results before rolling the query. `500` seems to be a good compromise.
* **per_call** *?bool* [`False`]: whether to yield once per API call or once per retrieved item.


### #.summary

Method that can be used to compile stats about the given link and optionally return the top 100 posts having shared the link.

```python
stats = client.summary('https://www.lemonde.fr', start_date='2019-01-01')

# If you want top posts
stats, posts = client.summary(
  'https://www.lemonde.fr',
  start_date='2019-01-01',
  with_top_posts=True
)
```

*Arguments*

* **link** *str*: url to query.
* **start_date** *str*: start date for the agregation.
* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.
* **sort_by** *?str* [`date`]: how to sort posts. Can be `date`, `subscriber_count` or `total_interactions`.
* **with_top_posts** *?bool*: whether to also return top 100 posts.


## FacebookMobileScraper

Scraper able to work on Facebook's oldest mobile version.

```python
from minet.facebook import FacebookMobileScraper

scraper = FacebookMobileScraper(cookie='chrome')

# If you want to be easier on the site to avoid soft bans
scraper = FacebookMobileScraper(cookie='chrome', throttle=2)
```

*Arguments*

* **cookie** *str*: Either the name of a browser you want to extract the relevant Facebook cookie from (example: `firefox`, `chrome`) or the string containing your Facebook cookie so the scraper can authenticate on the mobile website to be able to get the relevant pages to scrape.
* **throttle** *?float* [`0.5`]: time, in seconds, to wait between each call to the mobile website.

<h3 id="facebookmobilescraper-comments">#.comments</h3>

Method used to retrieve a post's comments.

```python
for comment in scraper.comments(post_url):
  print(comment)
```

*Arguments*

* **url** *str*: url of the post whose comments you want to scrape.
* **detailed** *?bool* [`False`]: whether to yield a detailed output containing some stats.
* **per_call** *?bool* [`False`]: whether to yield the list of comments retrieved per call to the website.
* **format** *?str* [`raw`]: either `raw` or `csv_row`.

## MediacloudClient

Client that can be used to access [Mediacloud](https://mediacloud.org/) APIs.

For more information about their API, check out their [documentation](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/api_2_0_spec.md) (for [topics](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/topics_api_2_0_spec.md) and for [admin](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/admin_api_2_0_spec.md)).

```python
from minet.mediacloud import MediacloudClient

client = MediacloudClient(token='MYAPIKEY')
```

### #.count

Method returning the number of stories matching a given query. Check out [#.search](#search) docs to read about its arguments etc.

<h3 id="mc-search">#.search</h3>

Method yielding all stories matching a given query.

```python
for story in client.search('andropov'):
  print(story)
```

*Arguments*

* **query** *str*: SOLR search query. To see how to query efficiently, check out those [docs](https://mediacloud.org/support/query-guide/) for more information.
* **collections** *?list<int|str>*: a list of collections where stories should be searched.
* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.

### #.topic_stories

Method yielding all of a given topic's stories.

```python
for story in client.topic_stories(4536):
  print(story)
```

*Arguments*

* **topic_id** *str*: id of target topic.
* **from_media_id** *?str*: return only stories linked from a media having this id.
* **media_id** *?str*: return only stories coming from a media having this id.
* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.
