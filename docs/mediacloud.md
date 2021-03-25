# Minet Library Mediacloud Utilities

Documentation for the utilities found in the `minet.mediacloud` subpackage.

## Summary

* [MediacloudAPIClient](#mediacloudapiclient)
  * [#.count](#count)
  * [#.search](#search)
  * [#.topic_stories](#topic_stories)

## MediacloudAPIClient

Client that can be used to access [Mediacloud](https://mediacloud.org/) APIs.

For more information about their API, check out their [documentation](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/api_2_0_spec.md) (for [topics](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/topics_api_2_0_spec.md) and for [admin](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/admin_api_2_0_spec.md)).

```python
from minet.mediacloud import MediacloudAPIClient

client = MediacloudAPIClient(token='MYAPIKEY')
```

### #.count

Method returning the number of stories matching a given query. Check out [#.search](#search) docs to read about its arguments etc.

### #.search

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
