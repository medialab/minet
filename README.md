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

* [multithreaded_fetch](#multithreaded_fetch)
* [multithreaded_resolve](#multithreaded_resolve)

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


```
usage: minet fetch [-h] [--contents-in-report] [-d OUTPUT_DIR] [-f FILENAME]
                   [--filename-template FILENAME_TEMPLATE] [-g {firefox,chrome}]
                   [-H HEADERS] [--standardize-encoding] [-o OUTPUT] [-s SELECT]
                   [-t THREADS] [--throttle THROTTLE] [--total TOTAL]
                   [--url-template URL_TEMPLATE] [-X METHOD]
                   column [file]

Minet Fetch Command
===================

Use multiple threads to fetch batches of urls from a CSV file. The
command outputs a CSV report with additional metadata about the
HTTP calls and will generally write the retrieved files in a folder
given by the user.

positional arguments:
  column                                          Column of the CSV file containing urls to fetch.
  file                                            CSV file containing the urls to fetch.

optional arguments:
  -h, --help                                      show this help message and exit
  --contents-in-report, --no-contents-in-report   Whether to include retrieved contents, e.g. html, directly in the report
                                                  and avoid writing them in a separate folder. This requires to standardize
                                                  encoding and won't work on binary formats.
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR          Directory where the fetched files will be written. Defaults to "content".
  -f FILENAME, --filename FILENAME                Name of the column used to build retrieved file names. Defaults to an uuid v4 with correct extension.
  --filename-template FILENAME_TEMPLATE           A template for the name of the fetched files.
  -g {firefox,chrome}, --grab-cookies {firefox,chrome}
                                                  Whether to attempt to grab cookies from your computer's browser.
  -H HEADERS, --header HEADERS                    Custom headers used with every requests.
  --standardize-encoding                          Whether to systematically convert retrieved text to UTF-8.
  -o OUTPUT, --output OUTPUT                      Path to the output report file. By default, the report will be printed to stdout.
  -s SELECT, --select SELECT                      Columns to include in report (separated by `,`).
  -t THREADS, --threads THREADS                   Number of threads to use. Defaults to 25.
  --throttle THROTTLE                             Time to wait - in seconds - between 2 calls to the same domain. Defaults to 0.2.
  --total TOTAL                                   Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.
  --url-template URL_TEMPLATE                     A template for the urls to fetch. Handy e.g. if you need to build urls from ids etc.
  -X METHOD, --request METHOD                     The http method to use. Will default to GET.

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
usage: minet extract [-h] [-e {dragnet,html2text}] [-i INPUT_DIRECTORY]
                     [-o OUTPUT] [-p PROCESSES] [-s SELECT] [--total TOTAL]
                     [report]

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
usage: minet scrape [-h] [-g GLOB] [-i INPUT_DIRECTORY] [-o OUTPUT]
                    [-p PROCESSES] [--total TOTAL]
                    scraper [report]

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
  -g GLOB, --glob GLOB                            Whether to scrape a bunch of html files on disk matched by a glob pattern rather than sourcing them from a CSV report.
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


```
usage: minet crowdtangle [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT] [-t TOKEN]
                         {leaderboard,lists,posts,search} ...

Minet Crowdtangle Command
=========================

Gather data from the CrowdTangle APIs easily and efficiently.

optional arguments:
  -h, --help                        show this help message and exit
  --rate-limit RATE_LIMIT           Authorized number of hits by minutes. Defaults to 6.
  -o OUTPUT, --output OUTPUT        Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN           CrowdTangle dashboard API token.

actions:
  {leaderboard,lists,posts,search}  Action to perform using the CrowdTangle API.

```


### leaderboard


```
usage: minet crowdtangle leaderboard [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT]
                                     [-t TOKEN] [--no-breakdown]
                                     [-f {csv,jsonl}] [-l LIMIT]
                                     [--list-id LIST_ID]

Minet CrowdTangle Leaderboard Command
=====================================

Gather information and aggregated stats about pages and groups of
the designated dashboard (indicated by a given token).

optional arguments:
  -h, --help                            show this help message and exit
  --rate-limit RATE_LIMIT               Authorized number of hits by minutes. Defaults to 6.
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
usage: minet crowdtangle lists [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT]
                               [-t TOKEN]

Minet CrowdTangle Lists Command
===============================

Retrieve the lists from a CrowdTangle dashboard (indicated by a
given token).

optional arguments:
  -h, --help                  show this help message and exit
  --rate-limit RATE_LIMIT     Authorized number of hits by minutes. Defaults to 6.
  -o OUTPUT, --output OUTPUT  Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN     CrowdTangle dashboard API token.

examples:

. Fetching a dashboard's lists:
    `minet ct lists --token YOUR_TOKEN > lists.csv`

```


### posts


```
usage: minet crowdtangle posts [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT]
                               [-t TOKEN] [--end-date END_DATE] [-f {csv,jsonl}]
                               [--language LANGUAGE] [-l LIMIT]
                               [--list-ids LIST_IDS]
                               [--partition-strategy PARTITION_STRATEGY]
                               [--resume]
                               [--sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}]
                               [--start-date START_DATE]
                               [--url-report URL_REPORT]

Minet CrowdTangle Posts Command
===============================

Gather post data from the designated dashboard (indicated by
a given token).

optional arguments:
  -h, --help                                      show this help message and exit
  --rate-limit RATE_LIMIT                         Authorized number of hits by minutes. Defaults to 6.
  -o OUTPUT, --output OUTPUT                      Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN                         CrowdTangle dashboard API token.
  --end-date END_DATE                             The latest date at which a post could be posted (UTC!).
  -f {csv,jsonl}, --format {csv,jsonl}            Output format. Defaults to `csv`.
  --language LANGUAGE                             Language of posts to retrieve.
  -l LIMIT, --limit LIMIT                         Maximum number of posts to retrieve. Will fetch every post by default.
  --list-ids LIST_IDS                             Ids of the lists from which to retrieve posts, separated by commas.
  --partition-strategy PARTITION_STRATEGY         Query partition strategy to use to overcome the API search result limits. Should either be `day` or a number of posts.
  --resume                                        Whether to resume an interrupted collection. Requires -o/--output & --sort-by date
  --sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}
                                                  The order in which to retrieve posts. Defaults to `date`.
  --start-date START_DATE                         The earliest date at which a post could be posted (UTC!).
  --url-report URL_REPORT                         Path to an optional report file to write about urls found in posts.

examples:

. Fetching the 500 most latest posts from a dashboard:
    `minet ct posts --token YOUR_TOKEN --limit 500 > latest-posts.csv`

```


### search


```
usage: minet crowdtangle posts [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT]
                               [-t TOKEN] [--end-date END_DATE] [-f {csv,jsonl}]
                               [--language LANGUAGE] [-l LIMIT]
                               [--list-ids LIST_IDS]
                               [--partition-strategy PARTITION_STRATEGY]
                               [--resume]
                               [--sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}]
                               [--start-date START_DATE]
                               [--url-report URL_REPORT]

Minet CrowdTangle Posts Command
===============================

Gather post data from the designated dashboard (indicated by
a given token).

optional arguments:
  -h, --help                                      show this help message and exit
  --rate-limit RATE_LIMIT                         Authorized number of hits by minutes. Defaults to 6.
  -o OUTPUT, --output OUTPUT                      Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN                         CrowdTangle dashboard API token.
  --end-date END_DATE                             The latest date at which a post could be posted (UTC!).
  -f {csv,jsonl}, --format {csv,jsonl}            Output format. Defaults to `csv`.
  --language LANGUAGE                             Language of posts to retrieve.
  -l LIMIT, --limit LIMIT                         Maximum number of posts to retrieve. Will fetch every post by default.
  --list-ids LIST_IDS                             Ids of the lists from which to retrieve posts, separated by commas.
  --partition-strategy PARTITION_STRATEGY         Query partition strategy to use to overcome the API search result limits. Should either be `day` or a number of posts.
  --resume                                        Whether to resume an interrupted collection. Requires -o/--output & --sort-by date
  --sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}
                                                  The order in which to retrieve posts. Defaults to `date`.
  --start-date START_DATE                         The earliest date at which a post could be posted (UTC!).
  --url-report URL_REPORT                         Path to an optional report file to write about urls found in posts.

examples:

. Fetching the 500 most latest posts from a dashboard:
    `minet ct posts --token YOUR_TOKEN --limit 500 > latest-posts.csv`

```


## Facebook


```
usage: minet facebook [-h] {comments} ...

Minet Facebook Command
======================

Collects data from Facebook.

optional arguments:
  -h, --help  show this help message and exit

actions:
  {comments}  Action to perform to collect data on Facebook

```


### comments


```
usage: minet facebook comments [-h] [-c COOKIE] [-o OUTPUT] url

Minet Facebook Comments Command
===============================

Scrape series of comments on Facebook.

positional arguments:
  url                         Url of the post from which to scrape comments.

optional arguments:
  -h, --help                  show this help message and exit
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which to extract it (support "firefox" and "chrome").
  -o OUTPUT, --output OUTPUT  Path to the output report file. By default, the report will be printed to stdout.

examples:

. Fetching a dashboard's lists:
    `minet fb comments`

```


---

## API

## multithreaded_fetch

Function fetching urls in a multithreaded fashion.

```python
from minet import multithreaded_fetch

# Most basic usage
urls = ['https://google.com', 'https://twitter.com']

for result in multithreaded_fetch(urls):
  print(result.url, result.response.status)

# Using a list of dicts

urls = [
  {
    'url': 'https://google.com',
    'label': 'Google'
  },
  {
    'url': 'https://twitter.com',
    'label': 'Twitter'
  }
]

for result in multithreaded_fetch(urls, key=lambda x: x['url']):
  print(result.item['label'], result.response.status)
```

*Arguments*:

* **iterator** *iterable*: An iterator over urls or arbitrary items, if you provide a `key` argument along with it.
* **key** *?callable*: A function extracting the url to fetch from the items yielded by the provided iterator.
* **request_args** *?callable*: A function returning arguments to pass to the internal `request` helper for a call.
* **threads** *?int*: Number of threads to use. Defaults to `25`.
* **throttle** *?float|callable*: Per-domain throttle in seconds. Or a function taking the domain and current item and returning the throttle to apply. Defaults to `0.2`.
* **guess_extension** *?bool*: Whether to attempt to guess the resource's extension. Defaults to `True`.
* **guess_encoding** *?bool*: Whether to attempt to guess the resource's encoding. Defaults to `True`.
* **buffer_size** *?int*: Max number of items per domain to enqueue into memory in hope of finding a new domain that can be processed immediately. Defaults to 1.

*Yields*:

A `FetchWorkerResult` having the following attributes:

* **url** *?string*: the fetched url.
* **item** *any*: original item from the iterator.
* **error** *?Exception*: an error.
* **response** *?urllib3.HTTPResponse*: the http response.
* **meta** *?dict*: additional metadata:
  * **mime** *?string*: resource's mimetype.
  * **ext** *?string*: resource's extension.
  * **encoding** *?string*: resource's encoding.


## multithreaded_resolve

Function resolving url redirections in a multithreaded fashion.

```python
from minet import multithreaded_resolve

# Most basic usage
urls = ['https://bit.ly/whatever', 'https://t.co/whatever']

for result in multithreaded_resolve(urls):
  print(result.stack)

# Using a list of dicts

urls = [
  {
    'url': 'https://bit.ly/whatever',
    'label': 'Bit.ly'
  },
  {
    'url': 'https://t.co/whatever',
    'label': 'Twitter'
  }
]

for result in multithreaded_resolve(urls, key=lambda x: x['url']):
  print(result.stack)
```

*Arguments*:

* **iterator** *iterable*: An iterator over urls or arbitrary items, if you provide a `key` argument along with it.
* **key** *?callable*: A function extracting the url to fetch from the items yielded by the provided iterator.
* **resolve_args** *?callable*: A function returning arguments to pass to the internal `resolve` helper for a call.
* **threads** *?int*: Number of threads to use. Defaults to `25`.
* **throttle** *?float|callable*: Per-domain throttle in seconds. Or a function taking the domain and current item and returning the throttle to apply. Defaults to `0.2`.
* **max_redirects** *?int*: Max number of redirections to follow. Defaults to `5`.
* **follow_refresh_header** *?bool*: Whether to follow `Refresh` headers or not. Defaults to `True`.
* **follow_meta_refresh** *?bool*: Whether to follow meta refresh tags. It's more costly because we need to stream the start of the response's body and cannot rely on headers alone. Defaults to  `False`.
* **buffer_size** *?int*: Max number of items per domain to enqueue into memory in hope of finding a new domain that can be processed immediately. Defaults to 1.

*Yields*:

A `ResolveWorkerResult` having the following attributes:

* **url** *?string*: the fetched url.
* **item** *any*: original item from the iterator.
* **error** *?Exception*: an error.
* **stack** *?list*: the redirection stack.

