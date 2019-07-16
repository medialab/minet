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
  * [leaderboard](#leaderboard)
  * [lists](#lists)
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

```
Minet Extract Command
=====================

Use multiple processes to extract raw text from a batch of HTML files.
This command can either work on a `minet fetch` report or on a bunch
of files. It will output an augmented report with the extracted text.

positional arguments:
  report                                          Input CSV fetch action report file.

optional arguments:
  -h, --help                                      show this help message and exit
  -e {dragnet,html2text}, --extractor {dragnet,html2text}
                                                  Extraction engine to use. Defaults to `dragnet`.
  -i INPUT_DIRECTORY, --input-directory INPUT_DIRECTORY
                                                  Directory where the HTML files are stored. Defaults to "content".
  -o OUTPUT, --output OUTPUT                      Path to the output report file. By default, the report will be printed to stdout.
  -p PROCESSES, --processes PROCESSES             Number of processes to use. Defaults to 4.
  -s SELECT, --select SELECT                      Columns to include in report (separated by `,`).
  --total TOTAL                                   Total number of HTML documents. Necessary if you want to display a finite progress indicator.

examples:

. Extracting raw text from a `minet fetch` report:
    `minet extract report.csv > extracted.csv`

. Working on a report from stdin:
    `minet fetch url_column file.csv | minet extract > extracted.csv`

. Extracting raw text from a bunch of files:
    `minet extract --glob "./content/*.html" > extracted.csv`
```

## scrape

TODO: document the scraping DSL

```
Minet Scrape Command
====================

Use multiple processes to scrape data from a batch of HTML files.
This command can either work on a `minet fetch` report or on a bunch
of files. It will output the scraped items.

positional arguments:
  scraper                                         Path to a scraper definition file.
  report                                          Input CSV fetch action report file.

optional arguments:
  -h, --help                                      show this help message and exit
  -i INPUT_DIRECTORY, --input-directory INPUT_DIRECTORY
                                                  Directory where the HTML files are stored. Defaults to "content".
  -o OUTPUT, --output OUTPUT                      Path to the output report file. By default, the report will be printed to stdout.
  -p PROCESSES, --processes PROCESSES             Number of processes to use. Defaults to 4.
  --total TOTAL                                   Total number of HTML documents. Necessary if you want to display a finite progress indicator.

examples:

. Scraping item from a `minet fetch` report:
    `minet scrape scraper.json report.csv > scraped.csv`

. Working on a report from stdin:
    `minet fetch url_column file.csv | minet fetch scraper.json > scraped.csv`

. Scraping items from a bunch of files:
    `minet scrape scraper.json --glob "./content/*.html" > scraped.csv`
```

## CrowdTangle

### leaderboard

```
Minet CrowdTangle Leaderboard Command
=====================================

Gather information and aggregated stats about pages and groups of
the designated dashboard (indicated by a given token).

optional arguments:
  -h, --help                            show this help message and exit
  -o OUTPUT, --output OUTPUT            Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN               CrowdTangle dashboard API token.
  --no-breakdown                        Whether to skip statistics breakdown by post type in the CSV output.
  -f {csv,jsonl}, --format {csv,jsonl}  Output format. Defaults to `csv`.
  -l LIMIT, --limit LIMIT               Maximum number of posts to retrieve. Will fetch every post by default.
  --list-id LIST_ID                     Optional list id from which to retrieve accounts.

examples:

. Fetching accounts statistics for every account in your dashboard:
    `minet ct leaderboard --token YOUR_TOKEN > accounts-stats.csv`
```

### lists

```
Minet CrowdTangle Lists Command
===============================

Retrieve the lists from a CrowdTangle dashboard (indicated by a
given token).

optional arguments:
  -h, --help                  show this help message and exit
  -o OUTPUT, --output OUTPUT  Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN     CrowdTangle dashboard API token.

examples:

. Fetching a dashboard's lists:
    `minet ct lists --token YOUR_TOKEN > lists.csv`
```

### posts

```
Minet CrowdTangle Posts Command
===============================

Gather post data from the designated dashboard (indicated by
a given token).

optional arguments:
  -h, --help                                      show this help message and exit
  -o OUTPUT, --output OUTPUT                      Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN                         CrowdTangle dashboard API token.
  --end-date END_DATE                             The latest date at which a post could be posted (UTC!).
  -f {csv,jsonl}, --format {csv,jsonl}            Output format. Defaults to `csv`.
  --language LANGUAGE                             Language of posts to retrieve.
  -l LIMIT, --limit LIMIT                         Maximum number of posts to retrieve. Will fetch every post by default.
  --list-ids LIST_IDS                             Ids of the lists from which to retrieve posts, separated by commas.
  --sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}
                                                  The order in which to retrieve posts. Defaults to `date`.
  --start-date START_DATE                         The earliest date at which a post could be posted (UTC!).

examples:

. Fetching the 500 most latest posts from a dashboard:
    `minet ct posts --token YOUR_TOKEN --limit 500 > latest-posts.csv`
```
