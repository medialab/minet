[![Build Status](https://github.com/medialab/minet/workflows/Tests/badge.svg)](https://github.com/medialab/minet/actions) [![DOI](https://zenodo.org/badge/169059797.svg)](https://zenodo.org/badge/latestdoi/169059797) [![download number](https://static.pepy.tech/badge/minet)](https://pepy.tech/project/minet)

![Minet](img/minet.png)

**minet** is a webmining command line tool & library for python (>= 3.6) that can be used to collect and extract data from a large variety of web sources such as raw webpages, Facebook, CrowdTangle, YouTube, Twitter, Media Cloud etc.

It adopts a very simple approach to various webmining problems by letting you perform a variety of actions from the comfort of the command line. No database needed: raw CSV files should be sufficient to do most of the work.

In addition, **minet** also exposes its high-level programmatic interface as a python library so you can tweak its behavior at will.

**Shortcuts**: [Command line documentation](./docs/cli.md), [Python library documentation](./docs/lib.md).

## Summary

* [What it does](#what-it-does)
* [Documented use cases](#documented-use-cases)
* [Features (from a technical standpoint)](#features-from-a-technical-standpoint)
* [Installation](#installation)
* [Upgrading](#upgrading)
* [Uninstallation](#uninstallation)
* [Documentation](#documentation)
* [Contributing](#contributing)
* [How to cite](#how-to-cite)

## What it does

Minet can single-handedly:
* Extract URLs from a text file (or a table)
* Parse URLs (get useful information, with Facebook- and Youtube-specific stuff)
* Join two CSV files by matching the columns containing URLs
* From a list of URLs, resolve their redirections
  * ...and check their HTTP status
  * ...and download the HTML
  * ...and extract hyperlinks
  * ...and extract the text content and other metadata (title...)
  * ...and scrape structured data (using a declarative language to define your heuristics)
* Crawl (using a declarative language to define a browsing behavior, and what to harvest)
* Mine or search:
  * *[Buzzsumo](https://buzzsumo.com/)* (requires API acess)
  * *[Crowdtangle](https://www.crowdtangle.com/)* (requires API access)
  * *[Mediacloud](https://mediacloud.org/)* (requires free API access)
  * *[Twitter](https://twitter.com)* (requires free API access)
  * *[Youtube](https://www.youtube.com/)* (requires free API access)
* Scrape (without requiring special access):
  * *[Facebook](https://www.facebook.com/)*
  * *[Twitter](https://twitter.com)*
  * *[Google Drive](https://drive.google.com)* (spreadsheets etc.)
* Grab & dump cookies from your browser
* Dump *[Hyphe](https://hyphe.medialab.sciences-po.fr/)* data

## Documented use cases

* [Fetching a large amount of urls](./cookbook/fetch.md)
* [Joining 2 CSV files by urls](./cookbook/url_join.md)
* [Using minet from a Jupyter notebook](./cookbook/notebooks/Minet%20in%20a%20Jupyter%20notebook.ipynb) (*very useful to experiment with the tool or teach students*)
* [Downloading images associated with a given hashtag on Twitter](./cookbook/twitter_images.md)
* [Scraping DSL Tutorial](./cookbook/scraping_dsl.md)

## Features (from a technical standpoint)

* Multithreaded, memory-efficient fetching from the web.
* Multithreaded, scalable crawling using a comfy DSL.
* Multiprocessed raw text content extraction from HTML pages.
* Multiprocessed scraping from HTML pages using a comfy DSL.
* URL-related heuristics utilities such as extraction, normalization and matching.
* Data collection from various APIs such as [CrowdTangle](https://www.crowdtangle.com/).

## Installation

**minet** can be installed as a standalone CLI tool (currently only on mac >= 10.14, ubuntu & similar) by running the following command in your terminal:

```shell
curl -sSL https://raw.githubusercontent.com/medialab/minet/master/scripts/install.sh | bash
```

Don't trust us enough to pipe the result of a HTTP request into `bash`? We wouldn't either, so feel free to read the installation script [here](./scripts/install.sh) and run it on your end if you prefer.

On ubuntu & similar you might need to install `curl` and `unzip` before running the installation script if you don't already have it:

```shell
sudo apt-get install curl unzip
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

## Documentation

* [minet as a command line tool](./docs/cli.md)
* [minet as a python library](./docs/lib.md)

## Contributing

To contribute to **minet** you can check out [this](./CONTRIBUTING.md) documentation.

## How to cite

**minet** is published on [Zenodo](https://zenodo.org/) as [![DOI](https://zenodo.org/badge/169059797.svg)](https://zenodo.org/badge/latestdoi/169059797)

You can cite it thusly:

> Guillaume Plique, Pauline Breteau, Jules Farjas, Héloïse Théro, Jean Descamps, & Amélie Pellé. (2019, October 14). Minet, a webmining CLI tool & library for python. Zenodo. http://doi.org/10.5281/zenodo.4564399
