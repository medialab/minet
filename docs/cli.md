# Minet Command Line Usage

## Summary

*Global utilities*

* [-h/--help/help](#help-flag)
* [--version](#version-flag)

*Generic commands*

* [crawl](#crawl)
* [fetch](#fetch)
* [extract](#extract)
* [scrape](#scrape)
* [url-extract](#url-extract)
* [url-join](#url-join)
* [url-parse](#url-parse)

*Platform-related commands*

* [crowdtangle (ct)](#crowdtangle)
  * [leaderboard](#leaderboard)
  * [lists](#lists)
  * [posts-by-id](#posts-by-id)
  * [posts](#posts)
  * [search](#ct-search)
  * [summary](#summary)
* [facebook (fb)](#facebook)
  * [comments](#comments)
  * [url-parse](#facebook-url-parse)
* [hyphe](#hyphe)
  * [dump](#dump)
* [mediacloud (mc)](#mediacloud)
  * [search](#mc-search)
  * [topic](#topic)
    * [stories](#stories)
* [twitter](#twitter)
  * [followers](#followers)
  * [friends](#friends)
* [youtube (yt)](#youtube)
  * [comments](#comments)
  * [url-parse](#youtube-url-parse)
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

## crawl

```
usage: minet crawl [-h] [-d OUTPUT_DIR] [--resume] [--throttle THROTTLE] crawler

Minet Crawl Command
===================

Use multiple threads to crawl the web using minet crawling and
scraping DSL.

positional arguments:
  crawler                                 Path to the crawler definition file.

optional arguments:
  -h, --help                              show this help message and exit
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR  Output directory.
  --resume                                Whether to resume an interrupted crawl.
  --throttle THROTTLE                     Time to wait - in seconds - between 2 calls to the same domain. Defaults to 0.2.

examples:

. TODO:
    `minet crawl`

```

## fetch

```
usage: minet fetch [-h] [--compress] [--contents-in-report] [-d OUTPUT_DIR]
                   [-f FILENAME] [--filename-template FILENAME_TEMPLATE]
                   [-g {firefox,chrome}] [-H HEADERS] [--resume]
                   [--standardize-encoding] [-o OUTPUT] [-s SELECT] [-t THREADS]
                   [--throttle THROTTLE] [--total TOTAL]
                   [--url-template URL_TEMPLATE] [-X METHOD]
                   column [file]

Minet Fetch Command
===================

Use multiple threads to fetch batches of urls from a CSV file. The
command outputs a CSV report with additional metadata about the
HTTP calls and will generally write the retrieved files in a folder
given by the user.

positional arguments:
  column                                          Column of the CSV file containing urls to fetch or a single url to fetch.
  file                                            CSV file containing the urls to fetch.

optional arguments:
  -h, --help                                      show this help message and exit
  --compress                                      Whether to compress the contents.
  --contents-in-report, --no-contents-in-report   Whether to include retrieved contents, e.g. html, directly in the report
                                                  and avoid writing them in a separate folder. This requires to standardize
                                                  encoding and won't work on binary formats.
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR          Directory where the fetched files will be written. Defaults to "content".
  -f FILENAME, --filename FILENAME                Name of the column used to build retrieved file names. Defaults to an uuid v4 with correct extension.
  --filename-template FILENAME_TEMPLATE           A template for the name of the fetched files.
  -g {firefox,chrome}, --grab-cookies {firefox,chrome}
                                                  Whether to attempt to grab cookies from your computer's browser.
  -H HEADERS, --header HEADERS                    Custom headers used with every requests.
  --resume                                        Whether to resume from an aborted report.
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

For more documentation about minet's scraping DSL check this [page](../cookbook/scraping_dsl.md) from the Cookbook.

```
usage: minet scrape [-h] [-f {csv,jsonl}] [-g GLOB] [-i INPUT_DIRECTORY]
                    [-o OUTPUT] [-p PROCESSES] [--total TOTAL]
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
  -f {csv,jsonl}, --format {csv,jsonl}            Output format.
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
    `minet fetch url_column file.csv | minet scrape scraper.json > scraped.csv`

. Scraping a single page from the web:
    `minet fetch https://news.ycombinator.com/ | minet scrape scraper.json > scraped.csv`

. Scraping items from a bunch of files:
    `minet scrape scraper.json --glob "./content/*.html" > scraped.csv`

```

## url-extract

```
usage: minet url-extract [-h] [--base-url BASE_URL] [--from {text,html}]
                         [-o OUTPUT] [-s SELECT] [--total TOTAL]
                         column [file]

Minet Url Extract Command
=========================

Extract urls from a CSV column containing either raw text or raw
HTML.

positional arguments:
  column                      Name of the column containing text or html.
  file                        Target CSV file.

optional arguments:
  -h, --help                  show this help message and exit
  --base-url BASE_URL         Base url used to resolve relative urls.
  --from {text,html}          Extract urls from which kind of source?
  -o OUTPUT, --output OUTPUT  Path to the output file. By default, the result will be printed to stdout.
  -s SELECT, --select SELECT  Columns to keep in output, separated by comma.
  --total TOTAL               Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.

examples:

. Extracting urls from a text column:
    `minet url-extract text posts.csv > urls.csv`

. Extracting urls from a html column:
    `minet url-extract html --from html posts.csv > urls.csv`

```

## url-join

```
usage: minet url-join [-h] [-o OUTPUT] [-s SELECT] column1 file1 column2 file2

Minet Url Join Command
======================

Join two CSV files by matching them on columns containing urls. In
fact, the command will index the first file's urls into a
hierchical trie before attempting to match the second file's ones.

positional arguments:
  column1                     Name of the url column in the first file.
  file1                       Path to the first file.
  column2                     Name of the url column in the second file.
  file2                       Path to the second file.

optional arguments:
  -h, --help                  show this help message and exit
  -o OUTPUT, --output OUTPUT  Path to the output joined file. By default, the join will be printed to stdout.
  -s SELECT, --select SELECT  Columns from the first file to keep, separated by comma.

examples:

. Joining two files:
    `minet url-join url webentities.csv post_url posts.csv > joined.csv`

. Keeping only some columns from first file:
    `minet url-join url webentities.csv post_url posts.csv -s url,id > joined.csv`

```

## url-parse

```
usage: minet url-parse [-h] [-o OUTPUT] [-s SELECT] [--separator SEPARATOR]
                       [--strip-protocol] [--total TOTAL]
                       column [file]

Minet Url Parse Command
=======================

Overload a CSV file containing urls with a selection of additional
metadata such as their normalized version, domain name etc.

positional arguments:
  column                                 Name of the column containing urls.
  file                                   Target CSV file.

optional arguments:
  -h, --help                             show this help message and exit
  -o OUTPUT, --output OUTPUT             Path to the output file. By default, the result will be printed to stdout.
  -s SELECT, --select SELECT             Columns to keep in output, separated by comma.
  --separator SEPARATOR                  Split url column by a separator?
  --strip-protocol, --no-strip-protocol  Whether or not to strip the protocol when normalizing the url. Defaults to strip protocol.
  --total TOTAL                          Total number of lines in CSV file. Necessary if you want to display a finite progress indicator.

examples:

. Creating a report about a file's urls:
    `minet url-report url posts.csv > report.csv`

. Keeping only selected columns from the input file:
    `minet url-report url posts.csv -s id,url,title > report.csv`

. Multiple urls joined by separator:
    `minet url-report urls posts.csv --separator "|" > report.csv`

```

## CrowdTangle

```
usage: minet crowdtangle [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT] [-t TOKEN]
                         {leaderboard,lists,posts,posts-by-id,search,summary}
                         ...

Minet Crowdtangle Command
=========================

Gather data from the CrowdTangle APIs easily and efficiently.

optional arguments:
  -h, --help                                      show this help message and exit
  --rate-limit RATE_LIMIT                         Authorized number of hits by minutes. Defaults to 6.
  -o OUTPUT, --output OUTPUT                      Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN                         CrowdTangle dashboard API token.

actions:
  {leaderboard,lists,posts,posts-by-id,search,summary}
                                                  Action to perform using the CrowdTangle API.

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

### posts-by-id

```
usage: minet crowdtangle posts-by-id [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT]
                                     [-t TOKEN] [-s SELECT] [--resume]
                                     [--total TOTAL]
                                     column [file]

Minet CrowdTangle Post By Id Command
====================================

Retrieve metadata about batches of posts using Crowdtangle's API.

positional arguments:
  column                      Name of the column containing the posts URL or id in the CSV file.
  file                        CSV file containing the inquired URLs or ids.

optional arguments:
  -h, --help                  show this help message and exit
  --rate-limit RATE_LIMIT     Authorized number of hits by minutes. Defaults to 6.
  -o OUTPUT, --output OUTPUT  Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN     CrowdTangle dashboard API token.
  -s SELECT, --select SELECT  Columns to include in report (separated by `,`).
  --resume                    Whether to resume an aborted collection.
  --total TOTAL               Total number of posts. Necessary if you want to display a finite progress indicator.

examples:

. Retrieving information about a batch of posts:
    `minet ct posts-by-id post-url posts.csv --token YOUR_TOKEN > metadata.csv`

. Retrieving information about a single post:
    `minet ct posts-by-id 1784333048289665 --token YOUR_TOKEN`

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

examples:

. Fetching the 500 most latest posts from a dashboard:
    `minet ct posts --token YOUR_TOKEN --limit 500 > latest-posts.csv`

```

<h3 id="ct-search">search</h3>

```
usage: minet crowdtangle search [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT]
                                [-t TOKEN] [--and AND] [--end-date END_DATE]
                                [-f {csv,jsonl}] [--language LANGUAGE]
                                [-l LIMIT] [--not-in-title] [--offset OFFSET]
                                [--partition-strategy PARTITION_STRATEGY]
                                [-p PLATFORMS]
                                [--sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}]
                                [--start-date START_DATE] [--types TYPES]
                                terms

Minet CrowdTangle Search Command
================================

Search posts on the whole CrowdTangle platform.

More on Crowdtangle API docs here:
https://github.com/CrowdTangle/API/wiki/Search

positional arguments:
  terms                                           The search query term or terms.

optional arguments:
  -h, --help                                      show this help message and exit
  --rate-limit RATE_LIMIT                         Authorized number of hits by minutes. Defaults to 6.
  -o OUTPUT, --output OUTPUT                      Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN                         CrowdTangle dashboard API token.
  --and AND                                       AND clause to add to the query terms.
  --end-date END_DATE                             The latest date at which a post could be posted (UTC!).
  -f {csv,jsonl}, --format {csv,jsonl}            Output format. Defaults to `csv`.
  --language LANGUAGE                             Language ISO code like "fr" or "zh-CN".
  -l LIMIT, --limit LIMIT                         Maximum number of posts to retrieve. Will fetch every post by default.
  --not-in-title                                  Whether to search terms in account titles also.
  --offset OFFSET                                 Count offset.
  --partition-strategy PARTITION_STRATEGY         Query partition strategy to use to overcome the API search result limits. Should either be `day` or a number of posts.
  -p PLATFORMS, --platforms PLATFORMS             The platforms, separated by comma from which to retrieve posts.
  --sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}
                                                  The order in which to retrieve posts. Defaults to `date`.
  --start-date START_DATE                         The earliest date at which a post could be posted (UTC!).
  --types TYPES                                   Types of post to include, separated by comma.

examples:

. Fetching a dashboard's lists:
    `minet ct search --token YOUR_TOKEN > posts.csv`

```

### summary

```
usage: minet crowdtangle summary [-h] [--rate-limit RATE_LIMIT] [-o OUTPUT]
                                 [-t TOKEN] [--posts POSTS] [-s SELECT]
                                 [--sort-by {total_interactions,date,subscriber_count}]
                                 [--start-date START_DATE] [--total TOTAL]
                                 column [file]

Minet CrowdTangle Link Summary Command
======================================

Retrieve aggregated statistics about link sharing
on the Crowdtangle API and by platform.

positional arguments:
  column                                          Name of the column containing the URL in the CSV file.
  file                                            CSV file containing the inquired URLs.

optional arguments:
  -h, --help                                      show this help message and exit
  --rate-limit RATE_LIMIT                         Authorized number of hits by minutes. Defaults to 6.
  -o OUTPUT, --output OUTPUT                      Path to the output file. By default, everything will be printed to stdout.
  -t TOKEN, --token TOKEN                         CrowdTangle dashboard API token.
  --posts POSTS                                   Path to a file containing the retrieved posts.
  -s SELECT, --select SELECT                      Columns to include in report (separated by `,`).
  --sort-by {total_interactions,date,subscriber_count}
                                                  How to sort retrieved posts. Defaults to `date`.
  --start-date START_DATE                         The earliest date at which a post could be posted (UTC!).
  --total TOTAL                                   Total number of HTML documents. Necessary if you want to display a finite progress indicator.

examples:

. Computing a summary of aggregated stats for urls contained in a CSV row:
    `minet ct summary url urls.csv --token YOUR_TOKEN --start-date 2019-01-01 > summary.csv`

```

## Facebook

```
usage: minet facebook [-h] {comments,post-stats,url-parse} ...

Minet Facebook Command
======================

Collects data from Facebook.

optional arguments:
  -h, --help                       show this help message and exit

actions:
  {comments,post-stats,url-parse}  Action to perform to collect data on Facebook

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

<h3 id="facebook-url-parse">url-parse</h3>

```
usage: minet facebook url-parse [-h] [-o OUTPUT] [-s SELECT] column [file]

Parse Facebook URLs
===================

Extract informations from Facebook URLs

positional arguments:
  column                      Name of the column containing the URL in the CSV file.
  file                        CSV file containing the inquired URLs.

optional arguments:
  -h, --help                  show this help message and exit
  -o OUTPUT, --output OUTPUT  Path to the output report file. By default, the report will be printed to stdout.
  -s SELECT, --select SELECT  Columns to include in report (separated by `,`).

```

## Hyphe

### dump

```
usage: minet hyphe dump [-h] [-d OUTPUT_DIR] [--body] url corpus

Minet Hyphe Dump Command
========================

Command dumping page-level information from a given
Hyphe corpus.

positional arguments:
  url                                     Url of the Hyphe API.
  corpus                                  Id of the corpus.

optional arguments:
  -h, --help                              show this help message and exit
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR  Output directory for dumped files. Will default to some name based on corpus name.
  --body                                  Whether to download pages body.

examples:

. Dumping a corpus into the ./corpus directory:
    `minet hyphe dump http://myhyphe.com/api/ corpus-name -d corpus`

```

## Mediacloud

<h3 id="mc-search">search</h3>

```
usage: minet mediacloud search [-h] [-t TOKEN] [-o OUTPUT] [-c COLLECTIONS]
                               [--skip-count]
                               query

Minet Mediacloud Search Command
===============================

Search stories on the Mediacloud platform.

positional arguments:
  query                                      Search query.

optional arguments:
  -h, --help                                 show this help message and exit
  -t TOKEN, --token TOKEN                    Mediacloud API token (also called key).
  -o OUTPUT, --output OUTPUT                 Path to the output report file. By default, the report will be printed to stdout.
  -c COLLECTIONS, --collections COLLECTIONS  List of searched collections separated by commas.
  --skip-count                               Whether to skip the first API call counting the number of posts for the progress bar.

```

### topic

#### stories

```
usage: minet mediacloud topic stories [-h] [-t TOKEN] [-o OUTPUT]
                                      [--media-id MEDIA_ID]
                                      [--from-media-id FROM_MEDIA_ID]
                                      topic_id

Minet Mediacloud Topic Stories Command
======================================

Retrieves the list of stories from a mediacloud topic.

positional arguments:
  topic_id                       Id of the topic.

optional arguments:
  -h, --help                     show this help message and exit
  -t TOKEN, --token TOKEN        Mediacloud API token (also called key).
  -o OUTPUT, --output OUTPUT     Path to the output report file. By default, the report will be printed to stdout.
  --media-id MEDIA_ID            Return only stories belonging to the given media_ids.
  --from-media-id FROM_MEDIA_ID  Return only stories that are linked from stories in the given media_id.

```

## Twitter

### followers

```
usage: minet twitter followers [-h] [--api-key API_KEY]
                               [--api-secret-key API_SECRET_KEY]
                               [--access-token ACCESS_TOKEN]
                               [--access-token-secret ACCESS_TOKEN_SECRET]
                               [--id] [-o OUTPUT] [-s SELECT] [--resume]
                               [--total TOTAL]
                               column [file]

Minet Twitter Followers Command
===============================

Retrieve followers of given user.

positional arguments:
  column                                     Name of the column containing the Twitter account screen names.
  file                                       CSV file containing the inquired Twitter users.

optional arguments:
  -h, --help                                 show this help message and exit
  --api-key API_KEY                          Twitter API key.
  --api-secret-key API_SECRET_KEY            Twitter API secret key.
  --access-token ACCESS_TOKEN                Twitter API access token.
  --access-token-secret ACCESS_TOKEN_SECRET  Twitter API access token secret.
  --id                                       Whether to use Twitter user ids rather than screen names.
  -o OUTPUT, --output OUTPUT                 Path to the output file. By default, the result will be printed to stdout.
  -s SELECT, --select SELECT                 Columns to include in report (separated by `,`).
  --resume                                   Whether to resume an aborted collection.
  --total TOTAL                              Total number of accounts. Necessary if you want to display a finite progress indicator.

examples:

. Getting followers of a list of user:
    `minet tw friends screen_name users.csv > followers.csv`

```

### friends

```
usage: minet twitter friends [-h] [--api-key API_KEY]
                             [--api-secret-key API_SECRET_KEY]
                             [--access-token ACCESS_TOKEN]
                             [--access-token-secret ACCESS_TOKEN_SECRET] [--id]
                             [-o OUTPUT] [-s SELECT] [--resume] [--total TOTAL]
                             column [file]

Minet Twitter Friends Command
=============================

Retrieve friends, i.e. followed users, of given user.

positional arguments:
  column                                     Name of the column containing the Twitter account screen names.
  file                                       CSV file containing the inquired Twitter users.

optional arguments:
  -h, --help                                 show this help message and exit
  --api-key API_KEY                          Twitter API key.
  --api-secret-key API_SECRET_KEY            Twitter API secret key.
  --access-token ACCESS_TOKEN                Twitter API access token.
  --access-token-secret ACCESS_TOKEN_SECRET  Twitter API access token secret.
  --id                                       Whether to use Twitter user ids rather than screen names.
  -o OUTPUT, --output OUTPUT                 Path to the output file. By default, the result will be printed to stdout.
  -s SELECT, --select SELECT                 Columns to include in report (separated by `,`).
  --resume                                   Whether to resume an aborted collection.
  --total TOTAL                              Total number of accounts. Necessary if you want to display a finite progress indicator.

examples:

. Getting friends of a list of user:
    `minet tw friends screen_name users.csv > friends.csv`

```

## Youtube

### comments

```
usage: minet youtube comments [-h] [-o OUTPUT] [-k KEY] id

Youtube comments
================

Retrieve metadata about Youtube comments using the API.

positional arguments:
  id                          Youtube video's id.

optional arguments:
  -h, --help                  show this help message and exit
  -o OUTPUT, --output OUTPUT  Path to the output report file. By default, the report will be printed to stdout.
  -k KEY, --key KEY           YouTube API Data dashboard API key.

```

<h3 id="youtube-url-parse">url-parse</h3>

```
usage: minet youtube url-parse [-h] [-o OUTPUT] [-s SELECT] column [file]

Parse Youtube URLs
==================

Extract informations from Youtube URLs

positional arguments:
  column                      Name of the column containing the URL in the CSV file.
  file                        CSV file containing the inquired URLs.

optional arguments:
  -h, --help                  show this help message and exit
  -o OUTPUT, --output OUTPUT  Path to the output report file. By default, the report will be printed to stdout.
  -s SELECT, --select SELECT  Columns to include in report (separated by `,`).

```

### videos

```
usage: minet youtube videos [-h] [-o OUTPUT] [-s SELECT] [-k KEY] column [file]

Youtube videos
==============

Retrieve metadata about Youtube videos using the API.

positional arguments:
  column                      Name of the column containing the video's url or id.
  file                        CSV file containing the Youtube videos urls or ids.

optional arguments:
  -h, --help                  show this help message and exit
  -o OUTPUT, --output OUTPUT  Path to the output report file. By default, the report will be printed to stdout.
  -s SELECT, --select SELECT  Columns to include in report (separated by `,`).
  -k KEY, --key KEY           YouTube API Data dashboard API key.

```

