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
