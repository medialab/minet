[![Build Status](https://travis-ci.org/medialab/minet.svg)](https://travis-ci.org/medialab/minet)

![Minet](img/minet.png)

**minet** is webmining CLI tool & library for python. It adopts a lo-fi approach to various webmining problems by letting you perform a variety of actions from the comfort of your command line. No database needed: raw data files will get you going.

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

## Commands

* [fetch](#fetch)
* [extract](#extract)
* [scrape](#scrape)
* [CrowdTangle (ct)](#crowdtangle)
  * [posts](#posts)

## fetch

```
Minet Fetch Command
===================

Use multiple threads to fetch batches of urls from a CSV file. The
command outputs a CSV report with additional metadata about the
HTTP calls and will generally write the retrieved files in a folder
given by the user.

positional arguments:
  column                                  Column of the CSV file containing urls to fetch.
  file                                    CSV file containing the urls to fetch.

optional arguments:
  -h, --help                              show this help message and exit
  --contents-in-report                    Whether to include retrieved contents, e.g. html, directly in the report
                                          and avoid writing them in a separate folder. This requires to standardize
                                          encoding and won't work on binary formats.
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR  Directory where the fetched files will be written. Defaults to "content".
  -f FILENAME, --filename FILENAME        Name of the column used to build retrieved file names. Defaults to an uuid v4 with correct extension.
  --filename-template FILENAME_TEMPLATE   A template for the name of the fetched files.
  -g, --grab-cookies                      Whether to attempt to grab cookies from your computer's chrome browser.
  --standardize-encoding                  Whether to systematically convert retrieved text to UTF-8.
  -o OUTPUT, --output OUTPUT              Path to the output report file. By default, the report will be printed to stdout.
  -s SELECT, --select SELECT              Columns to include in report (separated by `,`).
  -t THREADS, --threads THREADS           Number of threads to use. Defaults to 25.
  --throttle THROTTLE                     Time to wait - in seconds - between 2 calls to the same domain. Defaults to 0.2.
  --total TOTAL                           Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.
  --url-template URL_TEMPLATE             A template for the urls to fetch. Handy e.g. if you need to build urls from ids etc.

examples:

. Fetching a batch of url from existing CSV file:
    `minet fetch url_column file.csv > report.csv`

. CSV input from stdin:
    `xsv select url_column file.csv | minet fetch url_column > report.csv`

. Fetching a single url, useful to pipe into `minet scrape`:
    `minet fetch http://google.com | minet scrape ./scrape.json > scraped.csv`
```

## extract

If you want to be able to use the `extract` command, you will need to install the [`dragnet`](https://github.com/dragnet-org/dragnet) library. Because it is a bit cumbersome to install, it's not included in `minet`'s dependencies yet.

Just run the following & in the same order (`dragnet` needs to have specific deps installed before it can be able to compile its native files):

```
pip install lxml numpy Cython
pip install dragnet
```

## scrape

## CrowdTangle

### posts
