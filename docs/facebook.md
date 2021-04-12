# Minet Library Facebook Utilities

Documentation for the utilities found in the `minet.facebook` subpackage.

## Summary

* [FacebookMobileScraper](#facebookmobilescraper)
  * [#.comments](#comments)
  * [#.posts](#posts)

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

### #.comments

Method used to retrieve a post's comments.

```python
for comment in scraper.comments(post_url):
  print(comment)
```

*Arguments*

* **url** *str*: url of the post whose comments you want to scrape.
* **detailed** *?bool* [`False`]: whether to yield a detailed output containing some stats.
* **per_call** *?bool* [`False`]: whether to yield the list of comments retrieved per call to the website.

### #.posts

Method used to retrieve a group's posts.

```python
for post in scraper.posts(group_url):
  print(post)
```

*Arguments*

* **url** *str*: url of the group whose posts you want to scrape.
