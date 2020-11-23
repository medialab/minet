[![Build Status](https://travis-ci.org/medialab/minet.svg)](https://travis-ci.org/medialab/minet)

![Minet](img/minet.png)

**minet** is a webmining CLI tool & library for python. It adopts a lo-fi approach to various webmining problems by letting you perform a variety of actions from the comfort of your command line. No database needed: raw data files will get you going.

In addition, **minet** also exposes its high-level programmatic interface as a library so you can tweak its behavior at will.

## Features

* Multithreaded, memory-efficient fetching from the web.
* Multithreaded, scalable crawling using a comfy DSL.
* Multiprocessed raw text content extraction from HTML pages.
* Multiprocessed scraping from HTML pages using a comfy DSL.
* URL-related heuristics utilities such as extraction, normalization and matching.
* Data collection from various APIs such as [CrowdTangle](https://www.crowdtangle.com/).

## Use cases

* Downloading large amount of urls very fast.
* Writing scrapers to extract structured data from HTML pages.
* Writing crawlers to automatically browse the web.
* Extract raw textual content from HTML pages.
* Normalize batches of urls contained in a CSV file to perform relevant aggregations (dropping irrelevant query items, extracting domain name etc.)
* Join two CSV files based on columns containing urls needing to be organized hierarchically.
* Collecting data from [CrowdTangle](https://www.crowdtangle.com/) API (to collect and search posts mainly from [Facebook](https://www.facebook.com/) and [Instagram](https://www.instagram.com/)).
* Collecting data from [Facebook](https://www.facebook.com/) (comments, likes etc.)
* Parsing [Facebook](https://www.facebook.com/) urls in a CSV file.
* Collecting data from [Twitter](https://twitter.com) (users, followers, followees etc.)
* Collecting data from [YouTube](https://www.youtube.com/) (captions, comments, video metadata etc.)
* Parsing [YouTube](https://www.youtube.com/) urls in a CSV file.
* Dumping a [Hyphe](https://hyphe.medialab.sciences-po.fr/) corpus.
* Collecting data from [Media Cloud](https://mediacloud.org/) (search stories, dump topics etc.).

## Installation

`minet` can be installed using pip:

```shell
pip install minet
```

## Cookbook

To learn how to use `minet` and understand how it may fit your use cases, you should definitely check out our [Cookbook](./cookbook).

## Usage

* [Using minet as a command line tool](./docs/cli.md)
* [Using minet as a python library](./docs/lib.md)
