# Minet Command Line Usage

## Summary

*Global utilities*

* [-h/--help/help](#help-flag)
* [--version](#version-flag)

*Generic commands*

* [crawl](#crawl)
* [fetch](#fetch)
* [extract](#extract)
* [scrape](#scrape)
* [url-extract](#url-extract)
* [url-join](#url-join)
* [url-parse](#url-parse)

*Platform-related commands*

* [crowdtangle (ct)](#crowdtangle)
  * [leaderboard](#leaderboard)
  * [lists](#lists)
  * [posts-by-id](#posts-by-id)
  * [posts](#posts)
  * [search](#ct-search)
  * [summary](#summary)
* [facebook (fb)](#facebook)
  * [comments](#comments)
  * [url-parse](#facebook-url-parse)
* [hyphe](#hyphe)
  * [dump](#dump)
* [mediacloud (mc)](#mediacloud)
  * [search](#mc-search)
  * [topic](#topic)
    * [stories](#stories)
* [twitter](#twitter)
  * [friends](#friends)
  * [followers](#followers)
* [youtube (yt)](#youtube)
  * [comments](#comments)
  * [url-parse](#youtube-url-parse)
  * [videos](#videos)


<h2 id="help-flag">-h/--help</h2>

If you need help about a command, don't hesitate to use the `-h/--help` flag or the `help` command:

```
minet ct posts -h
# or:
minet ct posts --help
# or
minet help ct posts
```

<h2 id="version-flag"></h2>

To check the installed version of `minet`, you can use the `--version` flag:

```
minet --version
>>> minet x.x.x
```

## crawl

<% crawl %>

## fetch

<% fetch %>

## extract

If you want to be able to use the `extract` command, you will need to install the [`dragnet`](https://github.com/dragnet-org/dragnet) library. Because it is a bit cumbersome to install, it's not included in `minet`'s dependencies yet.

Just run the following & in the same order (`dragnet` needs to have specific deps installed before it can be able to compile its native files):

```
pip install lxml numpy Cython
pip install dragnet
```

<% extract %>

## scrape

For more documentation about minet's scraping DSL check this [page](../cookbook/scraping_dsl.md) from the Cookbook.

<% scrape %>

## url-extract

<% url-extract %>

## url-join

<% url-join %>

## url-parse

<% url-parse %>

## CrowdTangle

<% ct %>

### leaderboard

<% ct/leaderboard %>

### lists

<% ct/lists %>

### posts-by-id

<% ct/posts-by-id %>

### posts

<% ct/posts %>

<h3 id="ct-search">search</h3>

<% ct/search %>

### summary

<% ct/summary %>

## Facebook

<% fb %>

### comments

<% fb/comments %>

<h3 id="facebook-url-parse">url-parse</h3>

<% fb/url-parse %>

## Hyphe

### dump

<% hyphe/dump %>

## Mediacloud

<h3 id="mc-search">search</h3>

<% mc/search %>

### topic

#### stories

<% mc/topic/stories %>

## Twitter

### friends

<% twitter/friends %>

### followers

<% twitter/followers %>

## Youtube

### comments

<% yt/comments %>

<h3 id="youtube-url-parse">url-parse</h3>

<% yt/url-parse %>

### videos

<% yt/videos %>
