# Minet Command Line Usage

## Summary

_Global utilities_

- [-h/--help/help](#h--help)
- [--version](#version)
- [minetrc config files](#minetrc-config-files)
- [minet environment variables](#minet-environment-variables)

_Generic commands_

- [cookies](#cookies)
- [crawl](#crawl)
- [focus-crawl](#focus-crawl)
- [fetch](#fetch)
- [extract](#extract)
- [resolve](#resolve)
- [scrape](#scrape)
- [screenshot](#screenshot)
- [url-extract](#url-extract)
- [url-join](#url-join)
- [url-parse](#url-parse)

_Platform-related commands_

- [buzzsumo (bz)](#buzzsumo)
  - [limit](#limit)
  - [domain-summary](#domain-summary)
  - [domain](#domain)
  - [exact-url](#exact-url)
- [crowdtangle (ct)](#crowdtangle)
  - [leaderboard](#leaderboard)
  - [lists](#lists)
  - [posts-by-id](#posts-by-id)
  - [posts](#posts)
  - [search](#search)
  - [summary](#summary)
- [facebook (fb)](#facebook)
  - [comments](#comments)
  - [post](#post)
  - [posts](#posts-1)
  - [post-authors](#post-authors)
  - [url-likes](#url-likes)
- [google](#google)
  - [sheets](#sheets)
- [hyphe](#hyphe)
  - [crawl](#crawl)
  - [declare](#declare)
  - [destroy](#destroy)
  - [dump](#dump)
  - [reset](#reset)
  - [tag](#tag)
- [instagram (insta)](#instagram)
  - [comments](#comments-1)
  - [hashtag](#hashtag)
  - [post-infos](#post-infos)
  - [user-followers](#user-followers)
  - [user-following](#user-following)
  - [user-infos](#user-infos)
  - [user-posts](#user-posts)
- [mediacloud (mc)](#mediacloud)
  - [medias](#medias)
  - [search](#search-1)
  - [topic](#topic)
    - [stories](#stories)
- [telegram (tl)](#telegram)
  - [channel-infos](#channel-infos)
  - [channel-messages](#channel-messages)
- [tiktok (tk)](#tiktok)
  - [search-videos](#search-videos)
- [twitter](#twitter)
  - [attrition](#attrition)
  - [followers](#followers)
  - [followers-you-know](#followers-you-know)
  - [friends](#friends)
  - [list-followers](#list-followers)
  - [list-members](#list-members)
  - [retweeters](#retweeters)
  - [scrape](#scrape-1)
  - [tweet-date](#tweet-date)
  - [tweet-search](#tweet-search)
  - [tweet-count](#tweet-count)
  - [tweets](#tweets)
  - [users](#users)
  - [user-search](#user-search)
  - [user-tweets](#user-tweets)
- [wikipedia (wiki)](#wikipedia)
  - [pageviews](#pageviews)
- [youtube (yt)](#youtube)
  - [captions](#captions)
  - [channel-videos](#channel-videos)
  - [channels](#channels)
  - [comments](#comments-2)
  - [search](#search-2)
  - [videos](#videos)

## -h/--help

If you need help about a command, don't hesitate to use the `-h/--help` flag or the `help` command:

```
minet ct posts -h
# or:
minet ct posts --help
# or
minet help ct posts
```

## --version

To check the installed version of `minet`, you can use the `--version` flag:

```
minet --version
>>> minet x.x.x
```

## minetrc config files

Minet supports configuration files so you can skip some tedious command line arguments that you would need to provide each time you call `minet` otherwise (such as `--token` for crowdtangle commands).

Those configuration files can be written in YAML or JSON and can either be passed to minet using the `--rcfile` argument or will be searched at the following paths (with this precedence):

- `./.minetrc{,.yml,.yaml,.json}`
- `~/.minetrc{,.yml,.yaml,.json}`

_Configuration file_

```yml
---
buzzsumo:
  token: "MY_BZ_TOKEN" # Used as --token for `minet bz` commands
crowdtangle:
  token: "MY_CT_TOKEN" # Used as --token for `minet ct` commands
  rate_limit: 10 # Used as --rate-limit for `minet ct` commands
facebook:
  cookie: "MY_FACEBOOK_COOKIE" # Used as --cookie for `minet fb` commands
instagram:
  cookie: "MY_INSTAGRAM_COOKIE" # Used as --cookie for `minet insta` commands
mediacloud:
  token: "MY_MC_TOKEN" # Used as --token for `minet mc` commands
tiktok:
  cookie: "MY_TIKTOK_COOKIE" # Used as --cookie for `minet tk` commands
twitter:
  cookie: "MY_TWITTER_COOKIE" # Used as --cookie for `minet tw scrape` command
  api_key: "MY_API_KEY" # Used as --api-key for `minet tw` commands
  api_secret_key: "MY_API_SECRET_KEY" # Used as --api-secret-key for `minet tw` commands
  access_token: "MY_ACCESS_TOKEN" # Used as --access-token for `minet tw` commands
  access_token_secret: "MY_ACCESS_TOKEN_SECRET" # Used as --access-token-secret for `minet tw` commands
youtube:
  key: "MY_YT_API_KEY" # Used as --key for `minet yt` commands
```

## minet environment variables

Alternatively you can also set some arguments using environment variables whose name starts with `MINET_` and followed by the proper key.

To build the name of the variable, first check what can be configured in a minet [rcfile](#minetrc-config-files) and build your variable name by joining its path using an underscore:

For instance, to override `facebook.cookie`, the variable will be `MINET_FACEBOOK_COOKIE`.

If one of the path's key already contains underscore, it will work all the same. So to override `twitter.api_key`, the variable will be `MINET_TWITTER_API_KEY`.

Note that the given variable will be cast to the proper type as if it was passed as a command line argument (for instance, `MINET_CROWDTANGLE_RATE_LIMIT` will correctly be cast as an integer).

Finally note that command line arguments and flags will take precedence over environment variables, and that environment variables will take precedence over any rcfile configuration, but you can of course mix and match.

## cookies

<% cookies %>

## crawl

<% crawl %>

## focus-crawl

<% focus-crawl %>

## fetch

<% fetch %>

## extract

<% extract %>

## resolve

<% resolve %>

## scrape

For more documentation about minet's scraping DSL check this [page](../cookbook/scraping_dsl.md) from the Cookbook.

<% scrape %>

## screenshot

<% screenshot %>

## url-extract

<% url-extract %>

## url-join

<% url-join %>

## url-parse

<% url-parse %>

## BuzzSumo

<% bz %>

### limit

<% bz/limit %>

### domain-summary

<% bz/domain-summary %>

### domain

<% bz/domain %>

### exact-url

<% bz/exact-url %>

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

### search

<% ct/search %>

### summary

<% ct/summary %>

## Facebook

<% fb %>

### comments

<% fb/comments %>

### post

<% fb/post %>

### posts

<% fb/posts %>

### post-authors

<% fb/post-authors %>

### url-likes

<% fb/url-likes %>

## Google

<% google %>

### sheets

<% google/sheets %>

## Hyphe

### crawl

<% hyphe/crawl %>

### declare

<% hyphe/declare %>

### destroy

<% hyphe/destroy %>

### dump

<% hyphe/dump %>

### reset

<% hyphe/reset %>

### tag

<% hyphe/tag %>

## Instagram

<% insta %>

### comments

<% insta/comments %>

### hashtag

<% insta/hashtag %>

### post-infos

<% insta/post-infos %>

### user-followers

<% insta/user-followers %>

### user-following

<% insta/user-following %>

### user-infos

<% insta/user-infos %>

### user-posts

<% insta/user-posts %>

## Mediacloud

### medias

<% mc/medias %>

### search

<% mc/search %>

### topic

#### stories

<% mc/topic/stories %>

## Telegram

### channel-infos

<% telegram/channel-infos %>

### channel-messages

<% telegram/channel-messages %>

## Tiktok

<% tk %>

### search-videos

<% tiktok/search-videos %>

## Twitter

### attrition

<% twitter/attrition %>

### followers

<% twitter/followers %>

### followers-you-know

<% twitter/followers-you-know %>

### friends

<% twitter/friends %>

### list-followers

<% twitter/list-followers %>

### list-members

<% twitter/list-members %>

### retweeters

<% twitter/retweeters %>

### scrape

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

## Wikipedia

### pageviews

<% wikipedia/pageviews %>

## Youtube

### captions

<% yt/captions %>

### channel-videos

<% yt/channel-videos %>

### channels

<% yt/channels %>

### comments

<% yt/comments %>

### search

<% yt/search %>

### videos

<% yt/videos %>
