[![Build Status](https://travis-ci.org/medialab/minet.svg)](https://travis-ci.org/medialab/minet)

![Minet](img/minet.png)

**minet** is webmining CLI tool & library for python. It adopts a lo-fi approach to various webmining problems by letting you perform a variety of actions from the comfort of your command line. No database needed: raw data files will get you going.

In addition, **minet** also exposes its high-level programmatic interface as a library so you can tweak its behavior at will.

## Features

* Multithreaded, memory-efficient fetching from the web.
* Multiprocessed raw text content extraction from HTML pages.
* Multiprocessed scraping from HTML pages using a comfy JSON DSL.
* Data collection from various APIs such as [CrowdTangle](https://www.crowdtangle.com/).

## Installation

`minet` can be installed using pip:

```shell
pip install minet
```

## Usage

### CLI

*Global utilities*

* [-h/--help/help](#help-flag)
* [--version](#version-flag)

*Basic commands*

* [fetch](#fetch)
* [extract](#extract)
* [scrape](#scrape)

*API-related commands*

* [crowdtangle (ct)](#crowdtangle)
  * [leaderboard](#leaderboard)
  * [lists](#lists)
  * [posts](#posts)
  * [search](#search)
* [facebook (fb)](#facebook)
  * [comments](#comments)

### API

TODO...

---

## CLI

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

TODO: document the scraping DSL

<% scrape %>

## CrowdTangle

<% ct %>

### leaderboard

<% ct/leaderboard %>

### lists

<% ct/lists %>

### posts

<% ct/posts %>

### search

<% ct/posts %>

## Facebook

<% fb %>

### comments

<% fb/comments %>

---

## API
