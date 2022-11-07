# Minet Command Line Usage

## Summary

*Global utilities*

* [-h/--help/help](#help-flag)
* [--version](#version-flag)
* [minetrc config files](#minetrc)
* [minet environment variables](#envvars)

*Generic commands*

* [cookies](#cookies)
* [crawl](#crawl)
* [fetch](#fetch)
* [extract](#extract)
* [resolve](#resolve)
* [scrape](#scrape)
* [url-extract](#url-extract)
* [url-join](#url-join)
* [url-parse](#url-parse)

*Platform-related commands*

* [buzzsumo (bz)](#buzzsumo)
  * [limit](#buzzsumo-limit)
  * [domain-summary](#buzzsumo-domain-summary)
  * [domain](#buzzsumo-domain)
* [crowdtangle (ct)](#crowdtangle)
  * [leaderboard](#leaderboard)
  * [lists](#lists)
  * [posts-by-id](#posts-by-id)
  * [posts](#posts)
  * [search](#ct-search)
  * [summary](#summary)
* [facebook (fb)](#facebook)
  * [comments](#facebook-comments)
  * [posts](#facebook-posts)
  * [post-authors](#facebook-post-authors)
  * [url-likes](#facebook-url-likes)
* [google](#google)
  * [sheets](#google-sheets)
* [hyphe](#hyphe)
  * [declare](#hyphe-declare)
  * [destroy](#hyphe-destroy)
  * [dump](#hyphe-dump)
  * [reset](#hyphe-reset)
  * [tag](#hyphe-tag)
* [mediacloud (mc)](#mediacloud)
  * [medias](#mc-medias)
  * [search](#mc-search)
  * [topic](#topic)
    * [stories](#stories)
* [telegram](#telegram)
  * [channel-infos](#channel-infos)
  * [channel-messages](#channel-messages)
* [twitter](#twitter)
  * [attrition](#attrition)
  * [followers](#followers)
  * [friends](#friends)
  * [list-followers](#list-followers)
  * [list-members](#list-members)
  * [retweeters](#retweeters)
  * [scrape](#twitter-scrape)
  * [tweet-date](#tweet-date)
  * [tweet-search](#tweet-search)
  * [tweet-count](#tweet-count)
  * [tweets](#tweets)
  * [users](#users)
  * [user-search](#user-search)
  * [user-tweets](#user-tweets)
* [youtube (yt)](#youtube)
  * [captions](#captions)
  * [channel-videos](#channel-videos)
  * [comments](#youtube-comments)
  * [search](#youtube-search)
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

<h2 id="minetrc">minetrc config files</h2>

Minet supports configuration files so you can skip some tedious command line arguments that you would need to provide each time you call `minet` otherwise (such as `--token` for crowdtangle commands).

Those configuration files can be written in YAML or JSON and can either be passed to minet using the `--rcfile` argument or will be searched at the following paths (with this precedence):

* `./.minetrc{,.yml,.yaml,.json}`
* `~/.minetrc{,.yml,.yaml,.json}`

*Configuration file*

```yml
---
buzzsumo:
  token: "MY_BZ_TOKEN" # Used as --token for `minet bz` commands
crowdtangle:
  token: "MY_CT_TOKEN" # Used as --token for `minet ct` commands
  rate_limit: 10 # Used as --rate-limit for `minet ct` commands
facebook:
  cookie: "MY_FACEBOOK_COOKIE" # Used as --cookie for `minet fb` commands
mediacloud:
  token: "MY_MC_TOKEN" # Used as --token for `minet mc` commands
twitter:
  api_key: "MY_API_KEY" # Used as --api-key for `minet tw` commands
  api_secret_key: "MY_API_SECRET_KEY" # Used as --api-secret-key for `minet tw` commands
  access_token: "MY_ACCESS_TOKEN" # Used as --access-token for `minet tw` commands
  access_token_secret: "MY_ACCESS_TOKEN_SECRET" # Used as --access-token-secret for `minet tw` commands
youtube:
  key: "MY_YT_API_KEY" # Used as --key for `minet yt` commands
```

<h2 id="envvars">minet environment variables</h2>

Alternatively you can also set some arguments using environment variables whose name starts with `MINET_` and followed by the proper key.

To build the name of the variable, first check what can be configured in a minet [rcfile](#minetrc) and build your variable name by joining its path using an underscore:

For instance, to override `facebook.cookie`, the variable will be `MINET_FACEBOOK_COOKIE`.

If one of the path's key already contains underscore, it will work all the same. So to override `twitter.api_key`, the variable will be `MINET_TWITTER_API_KEY`.

Note that the given variable will be cast to the proper type as if it was passed as a command line argument (for instance, `MINET_CROWDTANGLE_RATE_LIMIT` will correctly be cast as an integer).

Finally note that command line arguments and flags will take precedence over environment variables, and that environment variables will take precedence over any rcfile configuration, but you can of course mix and match.

## cookies

<% cookies %>

## crawl

<% crawl %>

## fetch

<% fetch %>

## extract

<% extract %>

## resolve

<% resolve %>

## scrape

For more documentation about minet's scraping DSL check this [page](../cookbook/scraping_dsl.md) from the Cookbook.

<% scrape %>

## url-extract

<% url-extract %>

## url-join

<% url-join %>

## url-parse

<% url-parse %>

## BuzzSumo

<% bz %>

<h3 id="buzzsumo-limit">limit</h3>

<% bz/limit %>

<h3 id="buzzsumo-domain-summary">domain-summary</h3>

<% bz/domain-summary %>

<h3 id="buzzsumo-domain">domain</h3>

<% bz/domain %>

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

<h3 id="facebook-comments">comments</h3>

<% fb/comments %>

<h3 id="facebook-posts">posts</h3>

<% fb/posts %>

<h3 id="facebook-post-authors">post-authors</h3>

<% fb/post-authors %>

<h3 id="facebook-url-likes">url-likes</h3>

<% fb/url-likes %>

## Google

<% google %>

<h3 id="google-sheets">sheets</h3>

<% google/sheets %>

## Hyphe

<h3 id="hyphe-declare">declare</h3>

<% hyphe/declare %>

<h3 id="hyphe-destroy">destroy</h3>

<% hyphe/destroy %>

<h3 id="hyphe-dump">dump</h3>

<% hyphe/dump %>

<h3 id="hyphe-reset">reset</h3>

<% hyphe/reset %>

<h3 id="hyphe-tag">tag</h3>

<% hyphe/tag %>

## Mediacloud

<h3 id="mc-medias">medias</h3>

<% mc/medias %>

<h3 id="mc-search">search</h3>

<% mc/search %>

### topic

#### stories

<% mc/topic/stories %>

## Telegram

### channel-infos

<% telegram/channel-infos %>

### channel-messages

<% telegram/channel-messages %>

## Twitter

### attrition

<% twitter/attrition %>

### followers

<% twitter/followers %>

### friends

<% twitter/friends %>

### list-followers

<% twitter/list-followers %>

### list-members

<% twitter/list-members %>

### retweeters

<% twitter/retweeters %>

<h3 id="twitter-scrape">scrape</h3>

<% twitter/scrape %>

### tweet-date

<% twitter/tweet-date %>

### tweet-search

<% twitter/tweet-search %>

### tweet-count

<% twitter/tweet-count %>

### tweets

<% twitter/tweets %>

### users

<% twitter/users %>

### user-search

<% twitter/user-search %>

### user-tweets

<% twitter/user-tweets %>

## Youtube

### captions

<% yt/captions %>

### channel-videos

<% yt/channel-videos %>

<h3 id="youtube-comments">comments</h3>

<% yt/comments %>

<h3 id="youtube-search">search</h3>

<% yt/search %>

### videos

<% yt/videos %>
