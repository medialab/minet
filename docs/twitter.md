# Minet Library Twitter Utilities

Documentation for the utilities found in the `minet.twitter` subpackage.

## Summary

* [TwitterAPIScraper](#twitterapiscraper)
  * [#.search](#search)

## TwitterAPIScraper

Scraper that can be used to collect tweets from Twitter's public facing search.

To be able to compose complex queries and for more details about Twitter search operators, check out their advanced search widget [here](https://twitter.com/search-advanced?f=live).

```python
from minet.twitter import TwitterAPIScraper

scraper = TwitterAPIScraper()
```

### #.search

Method yielding tweets matched by the given query.

```python
for tweet in scraper.search('from:medialab_ScPo'):
  print(tweet)
```

*Arguments*

* **query** *str*: the query to search.
* **limit** *?int*: maximum number of tweets to retrieve.
