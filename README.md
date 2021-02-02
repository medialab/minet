[![Build Status](https://github.com/medialab/minet/workflows/Tests/badge.svg)](https://github.com/medialab/minet/actions)

![Minet](img/minet.png)

**minet** is a webmining CLI tool & library for python that can be used to collect and extract data from a large variety of web sources such as raw webpages, Facebook, CrowdTangle, YouTube, Twitter, Media Cloud etc.

It adopts a lo-fi approach to various webmining problems by letting you perform a variety of actions from the comfort of your command line. No database needed: raw data files such as CSV should be sufficient to do the work.

In addition, **minet** also exposes its high-level programmatic interface as a python library so you can tweak its behavior at will.

## Use cases

* Downloading large amount of urls very fast. ([example](./cookbook/fetch.md))
* Writing scrapers to extract structured data from HTML pages.
* Writing crawlers to automatically browse the web.
* Extract raw text content from HTML pages. ([example](./cookbook/compendium.md#extract-raw-text-content-from-html-pages))
* Normalize batches of urls contained in a CSV file to perform relevant aggregations (dropping irrelevant query items, extracting domain name etc.) ([example](./cookbook/compendium.md#parsing-and-normalizing-urls))
* Join two CSV files based on columns containing urls needing to be organized hierarchically.
* Collecting data from [CrowdTangle](https://www.crowdtangle.com/) API (to collect and search posts mainly from [Facebook](https://www.facebook.com/) and [Instagram](https://www.instagram.com/)).
* Collecting data from [Facebook](https://www.facebook.com/) (comments, likes etc.)
* Parsing [Facebook](https://www.facebook.com/) urls in a CSV file.
* Collecting data from [Twitter](https://twitter.com) (users, followers, followees etc.)
* Scraping data (tweets etc.) from [Twitter](https://twitter.com)'s website public facing search API.
* Collecting data from [YouTube](https://www.youtube.com/) (captions, comments, video metadata etc.)
* Parsing [YouTube](https://www.youtube.com/) urls in a CSV file.
* Dumping a [Hyphe](https://hyphe.medialab.sciences-po.fr/) corpus.
* Collecting data from [Media Cloud](https://mediacloud.org/) (search stories, dump topics etc.).

## Features (from a technical standpoint)

* Multithreaded, memory-efficient fetching from the web.
* Multithreaded, scalable crawling using a comfy DSL.
* Multiprocessed raw text content extraction from HTML pages.
* Multiprocessed scraping from HTML pages using a comfy DSL.
* URL-related heuristics utilities such as extraction, normalization and matching.
* Data collection from various APIs such as [CrowdTangle](https://www.crowdtangle.com/).

## Installation

**minet** can be installed as a standalone CLI tool (currently only on mac, ubuntu & similar) by running the following command in your terminal:

```shell
curl -sSL https://raw.githubusercontent.com/medialab/minet/master/scripts/install.sh | bash
```

Don't trust us enough to pipe the result of a HTTP request into `bash`? We wouldn't either, so feel free to read the installation script [here](./scripts/install.sh) and run it on your end if you prefer.

On ubuntu & similar you might need to install curl before running the installation script if you don't already have it:

```shell
sudo apt-get install curl
```

Else, **minet** can be installed directly as a python CLI tool and library using pip:

```shell
pip install minet
```

If you need more help to install and use **minet** from scratch, you can check those [installation documents](./docs/install.md).

Finally if you want to install the standalone binaries by yourself (even for windows) you can find them in each release [here](https://github.com/medialab/minet/releases).

## Upgrading

To upgrade the standalone version, simply run the install script once again:

```shell
curl -sSL https://raw.githubusercontent.com/medialab/minet/master/scripts/install.sh | bash
```

To upgrade the python version you can use pip thusly:

```shell
pip install -U minet
```

## Uninstallation

To uninstall the standalone version:

```shell
curl -sSL https://raw.githubusercontent.com/medialab/minet/master/scripts/uninstall.sh | bash
```

To uninstall the python version:

```shell
pip uninstall minet
```

## Cookbook

To learn how to use **minet** and understand how it may fit your use cases, you should definitely check out our [Cookbook](./cookbook).

## Usage

* [Using minet as a command line tool](./docs/cli.md)
* [Using minet as a python library](./docs/lib.md)

## Contributing

To contribute to **minet** you can check out [this](./CONTRIBUTE.md) documentation.
