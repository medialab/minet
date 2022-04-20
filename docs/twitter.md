# Minet Library Twitter Utilities

Documentation for the utilities found in the `minet.twitter` subpackage.

## Summary

* [TwitterAPIScraper](#twitterapiscraper)
  * [#.search_tweets](#search_tweets)
  * [#.search_users](#search_users)

## TwitterAPIScraper

Scraper that can be used to collect tweets from Twitter's public facing search.

To be able to compose complex queries and for more details about Twitter search operators, check out their advanced search widget [here](https://twitter.com/search-advanced?f=live).

```python
from minet.twitter import TwitterAPIScraper

scraper = TwitterAPIScraper()
```

### #.search_tweets

Method yielding tweets matched by the given query.

```python
for tweet in scraper.search_tweets('from:medialab_ScPo'):
  print(tweet)
```

*Arguments*

* **query** *str*: the query to search.
* **limit** *?int*: maximum number of tweets to retrieve.

### #.search_users

Method yielding users matched by the given query. Note that this method will hit a hard limit set by Twitter, around ~1000.

```python
for user in scraper.search_users('cancer'):
  print(user)
```

*Arguments*

* **query** *str*: the query to search.
* **limit** *?int*: maximum number of users to retrieve.
