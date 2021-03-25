# Minet Library Crowdtangle Utilities

Documentation for the utilities found in the `minet.crowdtangle` subpackage.

## Summary

* [CrowdTangleAPIClient](#crowdtangleapiclient)
  * [#.leaderboard](#leaderboard)
  * [#.lists](#lists)
  * [#.post](#post)
  * [#.posts](#posts)
  * [#.search](#search)
  * [#.summary](#summary)

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
* **per_call** *?bool* [`False`]: whether to yield once per API call or once per retrieved item.

### #.lists

Method returning your dashboard's lists.

```python
lists = client.lists()
```

*Arguments*

* **format** *?str* [`csv_dict_row`]: output format. Can be either `raw` to return raw JSON output from the API, `csv_dict_row` to return items as `OrderedDict` or finally `csv_row` to return plain lists.

### #.post

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
* **per_call** *?bool* [`False`]: whether to yield once per API call or once per retrieved item.

### #.search

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

