# Minet Command Line Usage

## Summary

*Global utilities*

* [-h/--help/help](#help-flag)
* [--version](#version-flag)
* [minetrc config files](#minetrc)
* [minet environment variables](#envvars)

*Generic commands*

* [cookies](#cookies)
* [crawl](#crawl)
* [fetch](#fetch)
* [extract](#extract)
* [resolve](#resolve)
* [scrape](#scrape)
* [url-extract](#url-extract)
* [url-join](#url-join)
* [url-parse](#url-parse)

*Platform-related commands*

* [buzzsumo (bz)](#buzzsumo)
  * [limit](#buzzsumo-limit)
  * [domain-summary](#buzzsumo-domain-summary)
  * [domain](#buzzsumo-domain)
* [crowdtangle (ct)](#crowdtangle)
  * [leaderboard](#leaderboard)
  * [lists](#lists)
  * [posts-by-id](#posts-by-id)
  * [posts](#posts)
  * [search](#ct-search)
  * [summary](#summary)
* [facebook (fb)](#facebook)
  * [comments](#facebook-comments)
  * [post](#facebook-post)
  * [posts](#facebook-posts)
  * [post-authors](#facebook-post-authors)
  * [url-likes](#facebook-url-likes)
* [google](#google)
  * [sheets](#google-sheets)
* [hyphe](#hyphe)
  * [declare](#hyphe-declare)
  * [destroy](#hyphe-destroy)
  * [dump](#hyphe-dump)
  * [reset](#hyphe-reset)
  * [tag](#hyphe-tag)
* [instagram (insta)](#instagram)
  * [hashtag](#hashtag)
  * [user-followers](#user-followers)
  * [user-following](#user-following)
  * [user-infos](#user-infos)
  * [user-posts](#user-posts)
* [mediacloud (mc)](#mediacloud)
  * [medias](#mc-medias)
  * [search](#mc-search)
  * [topic](#topic)
    * [stories](#stories)
* [telegram (tl)](#telegram)
  * [channel-infos](#channel-infos)
  * [channel-messages](#channel-messages)
* [tiktok (tk)](#tiktok)
  * [search-videos](#search-videos)
* [twitter](#twitter)
  * [attrition](#attrition)
  * [followers](#followers)
  * [friends](#friends)
  * [list-followers](#list-followers)
  * [list-members](#list-members)
  * [retweeters](#retweeters)
  * [scrape](#twitter-scrape)
  * [tweet-date](#tweet-date)
  * [tweet-search](#tweet-search)
  * [tweet-count](#tweet-count)
  * [tweets](#tweets)
  * [users](#users)
  * [user-search](#user-search)
  * [user-tweets](#user-tweets)
* [youtube (yt)](#youtube)
  * [captions](#captions)
  * [channel-videos](#channel-videos)
  * [channels](#channels)
  * [comments](#youtube-comments)
  * [search](#youtube-search)
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

<h2 id="minetrc">minetrc config files</h2>

Minet supports configuration files so you can skip some tedious command line arguments that you would need to provide each time you call `minet` otherwise (such as `--token` for crowdtangle commands).

Those configuration files can be written in YAML or JSON and can either be passed to minet using the `--rcfile` argument or will be searched at the following paths (with this precedence):

* `./.minetrc{,.yml,.yaml,.json}`
* `~/.minetrc{,.yml,.yaml,.json}`

*Configuration file*

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
  api_key: "MY_API_KEY" # Used as --api-key for `minet tw` commands
  api_secret_key: "MY_API_SECRET_KEY" # Used as --api-secret-key for `minet tw` commands
  access_token: "MY_ACCESS_TOKEN" # Used as --access-token for `minet tw` commands
  access_token_secret: "MY_ACCESS_TOKEN_SECRET" # Used as --access-token-secret for `minet tw` commands
youtube:
  key: "MY_YT_API_KEY" # Used as --key for `minet yt` commands
```

<h2 id="envvars">minet environment variables</h2>

Alternatively you can also set some arguments using environment variables whose name starts with `MINET_` and followed by the proper key.

To build the name of the variable, first check what can be configured in a minet [rcfile](#minetrc) and build your variable name by joining its path using an underscore:

For instance, to override `facebook.cookie`, the variable will be `MINET_FACEBOOK_COOKIE`.

If one of the path's key already contains underscore, it will work all the same. So to override `twitter.api_key`, the variable will be `MINET_TWITTER_API_KEY`.

Note that the given variable will be cast to the proper type as if it was passed as a command line argument (for instance, `MINET_CROWDTANGLE_RATE_LIMIT` will correctly be cast as an integer).

Finally note that command line arguments and flags will take precedence over environment variables, and that environment variables will take precedence over any rcfile configuration, but you can of course mix and match.

## cookies

```
usage: minet cookies [-h] [--csv] [--url URL] [-o OUTPUT]
                     {chrome,chromium,edge,firefox,opera}

Minet Cookies Command
=====================

Grab cookies directly from your browsers to use them easily later
in python scripts, for instance.

positional arguments:
  {chrome,chromium,edge,firefox,opera}
                                Name of the browser from which to grab cookies.

optional arguments:
  --csv                         Whether to format the output as CSV. If --url is
                                set, will output the cookie's morsels as CSV.
  --url URL                     If given, only returns full cookie header value
                                for this url.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  -h, --help                    show this help message and exit

examples:

. Dumping cookie jar from firefox:
    $ minet cookies firefox > jar.txt

. Dumping cookies as CSV:
    $ minet cookies firefox --csv > cookies.csv

. Print cookie for lemonde.fr:
    $ minet cookies firefox --url https://www.lemonde.fr

. Dump cookie morsels for lemonde.fr as CSV:
    $ minet cookies firefox --url https://www.lemonde.fr --csv > morsels.csv
```

## crawl

```
usage: minet crawl [-h] [-O OUTPUT_DIR] [--resume] [--throttle THROTTLE]
                   [-o OUTPUT]
                   crawler

Minet Crawl Command
===================

Use multiple threads to crawl the web using minet crawling and
scraping DSL.

positional arguments:
  crawler                       Path to the crawler definition file.

optional arguments:
  -O OUTPUT_DIR, --output-dir OUTPUT_DIR
                                Output directory.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to 0.2.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume an interrupted crawl.
  -h, --help                    show this help message and exit

examples:

. Running a crawler definition:
    $ minet crawl crawler.yml -O crawl-data
```

## fetch

```
usage: minet fetch [-h] [--domain-parallelism DOMAIN_PARALLELISM]
                   [-g {chrome,chromium,edge,firefox,opera}] [-H HEADERS]
                   [--insecure] [--separator SEPARATOR] [-t THREADS]
                   [--throttle THROTTLE] [--timeout TIMEOUT]
                   [--url-template URL_TEMPLATE] [-X METHOD]
                   [--max-redirects MAX_REDIRECTS] [--compress]
                   [--contents-in-report] [-O OUTPUT_DIR] [-f FILENAME]
                   [--filename-template FILENAME_TEMPLATE]
                   [--folder-strategy FOLDER_STRATEGY] [--keep-failed-contents]
                   [--standardize-encoding] [-i INPUT] [-s SELECT]
                   [--total TOTAL] [--resume] [-o OUTPUT]
                   value_or_column_name

Minet Fetch Command
===================

Use multiple threads to fetch batches of urls from a CSV file. The
command outputs a CSV report with additional metadata about the
HTTP calls and will generally write the retrieved files in a folder
given by the user.

positional arguments:
  value_or_column_name          Single url to process or name of the CSV column
                                containing urls when using -i/--input.

optional arguments:
  --compress                    Whether to compress the contents.
  --contents-in-report, --no-contents-in-report
                                Whether to include retrieved contents, e.g.
                                html, directly in the report and avoid writing
                                them in a separate folder. This requires to
                                standardize encoding and won't work on binary
                                formats.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to 1
  -f FILENAME, --filename FILENAME
                                Name of the column used to build retrieved file
                                names. Defaults to a md5 hash of final url. If
                                the provided file names have no extension (e.g.
                                ".jpg", ".pdf", etc.) the correct extension will
                                be added depending on the file type.
  --filename-template FILENAME_TEMPLATE
                                A template for the name of the fetched files.
  --folder-strategy FOLDER_STRATEGY
                                Name of the strategy to be used to dispatch the
                                retrieved files into folders to alleviate issues
                                on some filesystems when a folder contains too
                                much files. Note that this will be applied on
                                top of --filename-template. Defaults to "flat".
                                All of the strategies are described at the end
                                of this help.
  -g {chrome,chromium,edge,firefox,opera}, --grab-cookies {chrome,chromium,edge,firefox,opera}
                                Whether to attempt to grab cookies from your
                                computer's browser (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
  -H HEADERS, --header HEADERS  Custom headers used with every requests.
  --insecure                    Whether to allow ssl errors when performing
                                requests or not.
  --keep-failed-contents        Whether to keep & write contents for failed
                                (i.e. non-200) http requests.
  --max-redirects MAX_REDIRECTS
                                Maximum number of redirections to follow before
                                breaking. Defaults to 5.
  -O OUTPUT_DIR, --output-dir OUTPUT_DIR
                                Directory where the fetched files will be
                                written. Defaults to "downloaded".
  -X METHOD, --request METHOD   The http method to use. Will default to GET.
  --separator SEPARATOR         Character used to split the url cell in the CSV
                                file, if this one can in fact contain multiple
                                urls.
  --standardize-encoding        Whether to systematically convert retrieved text
                                to UTF-8.
  -t THREADS, --threads THREADS
                                Number of threads to use. Defaults to 25.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to 0.2.
  --timeout TIMEOUT             Maximum time - in seconds - to spend for each
                                request before triggering a timeout. Defaults to
                                ~30s.
  --url-template URL_TEMPLATE   A template for the urls to fetch. Handy e.g. if
                                you need to build urls from ids etc.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the urls you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  -h, --help                    show this help message and exit

columns being added to the output:

. "index": index of the line in the original file (the output will be
    arbitrarily ordered since multiple requests are performed concurrently).
. "resolved": final resolved url (after solving redirects) if different
    from requested url.
. "status": HTTP status code of the request, e.g. 200, 404, 503 etc.
. "error": an error code if anything went wrong when performing the request.
. "filename": path to the downloaded file, relative to the folder given
    through -O/--output-dir.
. "mimetype": detected mimetype of the requested file.
. "encoding": detected encoding of the requested file if relevant.
. "raw_contents": if --contents-in-report is set, will contain the
    downloaded text and the file won't be written.

--folder-strategy options:

. "flat": default choice, all files will be written in the indicated
    content folder.

. "prefix-x": e.g. "prefix-4", files will be written in folders
    having a name that is the first x characters of the file's name.
    This is an efficient way to partition content into folders containing
    roughly the same number of files if the file names are random (which
    is the case by default since md5 hashes will be used).

. "hostname": files will be written in folders based on their url's
    full host name.

. "normalized-hostname": files will be written in folders based on
    their url's hostname stripped of some undesirable parts (such as
    "www.", or "m." or "fr.", for instance).

examples:

. Fetching a batch of url from existing CSV file:
    $ minet fetch url_column file.csv > report.csv

. CSV input from stdin (mind the `-`):
    $ xsv select url_column file.csv | minet fetch url_column -i i > report.csv

. Fetching a single url, useful to pipe into `minet scrape`:
    $ minet fetch http://google.com | minet scrape ./scrape.json - > scraped.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## extract

```
usage: minet extract [-h] [-g GLOB] [-I INPUT_DIR] [-p PROCESSES] [-s SELECT]
                     [--total TOTAL] [-o OUTPUT]
                     report_or_glob_pattern

Minet Extract Command
=====================

Use multiple processes to extract raw content and various metadata
from a batch of HTML files. This command can either work on a
`minet fetch` report or on a bunch of files. It will output an
augmented report with the extracted text.

Extraction is performed using the `trafilatura` library by Adrien
Barbaresi. More information about the library can be found here:
https://github.com/adbar/trafilatura

Note that this methodology mainly targets news article and may fail
to extract relevant content from other kind of web pages.

positional arguments:
  report_or_glob_pattern        Report CSV file from `minet fetch` or glob
                                pattern if used with --glob. Will understand `-`
                                as stdin.

optional arguments:
  -g GLOB, --glob GLOB          Whether to extract text from a bunch of html
                                files on disk matched by a glob pattern rather
                                than sourcing them from a CSV report.
  -I INPUT_DIR, --input-dir INPUT_DIR
                                Directory where the HTML files are stored.
                                Defaults to "downloaded" if --glob is not set.
  -p PROCESSES, --processes PROCESSES
                                Number of processes to use. Defaults to roughly
                                half of the available CPUs.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  -h, --help                    show this help message and exit

columns being added to the output:

. "extract_error": any error that happened when extracting content.
. "canonical_url": canonical url of target html, extracted from
    link[rel=canonical].
. "title": title of the web page, from <title> usually.
. "description": description of the web page, as found in its
    metadata.
. "raw_content": main content of the web page as extracted.
. "comments": comment text whenever the heuristics succeeds in
    identifying them.
. "author": inferred author of the web page article when found in
    its metadata.
. "categories": list of categories extracted from the web page's
    metadata, separated by "|".
. "tags": list of tags extracted from the web page's metadata,
    separated by "|".
. "date": date of publication of the web page article when found in
    its metadata.
. "sitename": canonical name as declared by the website.

examples:

. Extracting text from a `minet fetch` report:
    $ minet extract report.csv > extracted.csv

. Extracting text from a bunch of files using a glob pattern:
    $ minet extract --glob "./content/**/*.html" > extracted.csv

. Working on a report from stdin (mind the `-`):
    $ minet fetch url_column file.csv | minet extract - > extracted.csv
```

## resolve

```
usage: minet resolve [-h] [--domain-parallelism DOMAIN_PARALLELISM]
                     [-g {chrome,chromium,edge,firefox,opera}] [-H HEADERS]
                     [--insecure] [--separator SEPARATOR] [-t THREADS]
                     [--throttle THROTTLE] [--timeout TIMEOUT]
                     [--url-template URL_TEMPLATE] [-X METHOD]
                     [--max-redirects MAX_REDIRECTS] [--follow-meta-refresh]
                     [--follow-js-relocation] [--infer-redirection]
                     [--canonicalize] [--only-shortened] [-i INPUT] [-s SELECT]
                     [--total TOTAL] [--resume] [-o OUTPUT]
                     value_or_column_name

Minet Resolve Command
=====================

Use multiple threads to resolve batches of urls from a CSV file. The
command outputs a CSV report with additional metadata about the
HTTP calls and the followed redirections.

positional arguments:
  value_or_column_name          Single url to process or name of the CSV column
                                containing urls when using -i/--input.

optional arguments:
  --canonicalize                Whether to extract the canonical url from the
                                html source code of the web page if found.
                                Requires to buffer part of the response body, so
                                it will slow things down.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to 1
  --follow-js-relocation        Whether to follow typical JavaScript window
                                relocation. Requires to buffer part of the
                                response body, so it will slow things down.
  --follow-meta-refresh         Whether to follow meta refresh tags. Requires to
                                buffer part of the response body, so it will
                                slow things down.
  -g {chrome,chromium,edge,firefox,opera}, --grab-cookies {chrome,chromium,edge,firefox,opera}
                                Whether to attempt to grab cookies from your
                                computer's browser (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
  -H HEADERS, --header HEADERS  Custom headers used with every requests.
  --infer-redirection           Whether to try to heuristically infer
                                redirections from the urls themselves, without
                                requiring a HTTP call.
  --insecure                    Whether to allow ssl errors when performing
                                requests or not.
  --max-redirects MAX_REDIRECTS
                                Maximum number of redirections to follow before
                                breaking. Defaults to 20.
  --only-shortened              Whether to only attempt to resolve urls that are
                                probably shortened.
  -X METHOD, --request METHOD   The http method to use. Will default to GET.
  --separator SEPARATOR         Character used to split the url cell in the CSV
                                file, if this one can in fact contain multiple
                                urls.
  -t THREADS, --threads THREADS
                                Number of threads to use. Defaults to 25.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to 0.2.
  --timeout TIMEOUT             Maximum time - in seconds - to spend for each
                                request before triggering a timeout. Defaults to
                                ~30s.
  --url-template URL_TEMPLATE   A template for the urls to fetch. Handy e.g. if
                                you need to build urls from ids etc.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the urls you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  -h, --help                    show this help message and exit

columns being added to the output:

. "resolved": final resolved url (after solving redirects).
. "status": HTTP status code of the request, e.g. 200, 404, 503 etc.
. "error": an error code if anything went wrong when performing the request.
. "redirects": total number of redirections to reach the final url.
. "chain": list of redirection types separated by "|".

examples:

. Resolving a batch of url from existing CSV file:
    $ minet resolve url_column file.csv > report.csv

. CSV input from stdin (mind the `-`):
    $ xsv select url_column file.csv | minet resolve url_column - > report.csv

. Resolving a single url:
    $ minet resolve https://lemonde.fr

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## scrape

For more documentation about minet's scraping DSL check this [page](../cookbook/scraping_dsl.md) from the Cookbook.

```
usage: minet scrape [-h] [-f {csv,jsonl}] [-g GLOB] [-I INPUT_DIR]
                    [-p PROCESSES] [--separator SEPARATOR] [--strain STRAIN]
                    [--validate] [--total TOTAL] [-o OUTPUT]
                    scraper report

Minet Scrape Command
====================

Use multiple processes to scrape data from a batch of HTML files.
This command can either work on a `minet fetch` report or on a bunch
of files filtered using a glob pattern.

It will output the scraped items as a CSV file.

positional arguments:
  scraper                       Path to a scraper definition file.
  report                        Report CSV file from `minet fetch`. Will
                                understand `-` as stdin.

optional arguments:
  -f {csv,jsonl}, --format {csv,jsonl}
                                Output format.
  -g GLOB, --glob GLOB          Whether to scrape a bunch of html files on disk
                                matched by a glob pattern rather than sourcing
                                them from a CSV report.
  -I INPUT_DIR, --input-dir INPUT_DIR
                                Directory where the HTML files are stored.
                                Defaults to "downloaded".
  -p PROCESSES, --processes PROCESSES
                                Number of processes to use. Defaults to roughly
                                half of the available CPUs.
  --separator SEPARATOR         Separator use to join lists of values when
                                output format is CSV. Defaults to "|".
  --strain STRAIN               Optional CSS selector used to strain, i.e. only
                                parse matched tags in the parsed html files in
                                order to optimize performance.
  --validate                    Just validate the given scraper then exit.
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  -h, --help                    show this help message and exit

examples:

. Scraping item from a `minet fetch` report:
    $ minet scrape scraper.yml report.csv > scraped.csv

. Working on a report from stdin (mind the `-`):
    $ minet fetch url_column file.csv | minet scrape scraper.yml - > scraped.csv

. Scraping a single page from the web:
    $ minet fetch https://news.ycombinator.com/ | minet scrape scraper.yml - > scraped.csv

. Scraping items from a bunch of files:
    $ minet scrape scraper.yml --glob "./content/**/*.html" > scraped.csv

. Yielding items as newline-delimited JSON (jsonl):
    $ minet scrape scraper.yml report.csv --format jsonl > scraped.jsonl

. Only validating the scraper definition and exit:
    $ minet scraper --validate scraper.yml

. Using a strainer to optimize performance:
    $ minet scraper links-scraper.yml --strain "a[href]" report.csv > links.csv
```

## url-extract

```
usage: minet url-extract [-h] [--base-url BASE_URL] [--from {html,text}]
                         [-s SELECT] [--total TOTAL] [-o OUTPUT]
                         column input

Minet Url Extract Command
=========================

Extract urls from a CSV column containing either raw text or raw
HTML.

positional arguments:
  column                      Name of the column containing text or html.
  input                       Target CSV file.

optional arguments:
  --base-url BASE_URL         Base url used to resolve relative urls.
  --from {html,text}          Extract urls from which kind of source?
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:

. Extracting urls from a text column:
    $ minet url-extract text posts.csv > urls.csv

. Extracting urls from a html column:
    $ minet url-extract html --from html posts.csv > urls.csv
```

## url-join

```
usage: minet url-join [-h] [-p MATCH_COLUMN_PREFIX] [--separator SEPARATOR]
                      [-s SELECT] [-o OUTPUT]
                      column1 input1 column2 input2

Minet Url Join Command
======================

Join two CSV files by matching them on columns containing urls. It
works by indexing the first file's urls in a specialized
URL trie to match them with the second file's urls.

positional arguments:
  column1                       Name of the column containing urls in the
                                indexed file.
  input1                        Path to the file to index. Will understand `-`
                                as stdin.
  column2                       Name of the column containing urls in the second
                                file.
  input2                        Path to the second file. Will understand `-` as
                                stdin.

optional arguments:
  -p MATCH_COLUMN_PREFIX, --match-column-prefix MATCH_COLUMN_PREFIX
                                Optional prefix to add to the first file's
                                column names to avoid conflicts.
  --separator SEPARATOR         Split indexed url column by a separator?
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  -h, --help                    show this help message and exit

examples:

. Joining two files:
    $ minet url-join url webentities.csv post_url posts.csv > joined.csv

. Adding a prefix to first file's column names:
    $ minet url-join -p w_ url webentities.csv post_url posts.csv > joined.csv

. Keeping only some columns from first file:
    $ minet url-join url webentities.csv post_url posts.csv -s url,id > joined.csv

. Reading one of the files from stdin:
    $ xsv select url webentities.csv | minet url-join url - post_url posts.csv > joined.csv
```

## url-parse

```
usage: minet url-parse [-h] [--separator SEPARATOR] [--facebook] [--twitter]
                       [--youtube] [--infer-redirection] [--fix-common-mistakes]
                       [--normalize-amp] [--quoted] [--sort-query]
                       [--strip-authentication] [--strip-fragment]
                       [--strip-index] [--strip-irrelevant-subdomains]
                       [--strip-lang-query-items] [--strip-lang-subdomains]
                       [--strip-protocol] [--strip-trailing-slash] [-i INPUT]
                       [-s SELECT] [--total TOTAL] [-o OUTPUT]
                       value_or_column_name

Minet Url Parse Command
=======================

Parse the urls contained in a CSV file using the python `ural`
library to extract useful information about them such as their
normalized version, domain name, etc.

positional arguments:
  value_or_column_name          Single url to process or name of the CSV column
                                containing urls when using -i/--input.

optional arguments:
  --facebook                    Whether to consider and parse the given urls as
                                coming from Facebook.
  --fix-common-mistakes, --dont-fix-common-mistakes
                                Whether or not to attempt to fix common URL
                                mistakes when normalizing url. Defaults to fix
                                common mistakes.
  --infer-redirection, --dont-infer-redirection
                                Whether or not to attempt resolving common
                                redirects by leveraging well-known GET
                                parameters when normalizing url. Defaults to
                                infer redirection.
  --normalize-amp, --dont-normalize-amp
                                Whether or not to attempt to normalize Google
                                AMP urls when normalizing url. Defaults to
                                normalize amp.
  --quoted, --no-quoted         Whether or not to normalize to a quoted or
                                unquoted version of the url when normalizing
                                url. Defaults to quoted.
  --separator SEPARATOR         Split url column by a separator?
  --sort-query, --dont-sort-query
                                Whether or not to sort query items when
                                normalizing url. Defaults to sort query.
  --strip-authentication, --dont-strip-authentication
                                Whether or not to strip authentication when
                                normalizing url. Defaults to strip
                                authentication.
  --strip-fragment, --dont-strip-fragment, --strip-fragment-except-routing
                                Whether or not to strip the url's fragment when
                                normalizing url. If set to `--strip-fragment-
                                except-routing`, will only strip the fragment if
                                the fragment is not deemed to be js routing
                                (i.e. if it contains a `/`). Defaults to strip
                                fragment except routing.
  --strip-index, --dont-strip-index
                                Whether or not to strip trailing index when
                                normalizing url. Defaults to strip index.
  --strip-irrelevant-subdomains, --dont-strip-irrelevant-subdomains
                                Whether or not to strip trailing irrelevant-
                                subdomains such as `www` etc. when normalizing
                                url. Defaults to no strip irrelevantsubdomains.
  --strip-lang-query-items, --dont-strip-lang-query-items
                                Whether or not to strip language query items
                                (ex: `gl=pt_BR`) when normalizing url. Defaults
                                to no strip lang query items.
  --strip-lang-subdomains, --dont-strip-lang-subdomains
                                Whether or not to strip language subdomains (ex:
                                `fr-FR.lemonde.fr` to only `lemonde.fr` because
                                `fr-FR` isn't a relevant subdomain, it indicates
                                the language and the country) when normalizing
                                url. Defaults to no strip lang subdomains.
  --strip-protocol, --dont-strip-protocol
                                Whether or not to strip the protocol when
                                normalizing the url. Defaults to strip protocol.
  --strip-trailing-slash, --dont-strip-trailing-slash
                                Whether or not to trailing slash when
                                normalizing url. Defaults to strip trailing
                                slash.
  --twitter                     Whether to consider and parse the given urls as
                                coming from Twitter.
  --youtube                     Whether to consider and parse the given urls as
                                coming from YouTube.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the urls you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  -h, --help                    show this help message and exit

columns being added to the output:

. "normalized_url": urls aggressively normalized by removing any part
  that is not useful to determine which resource it is actually
  pointing at.
. "inferred_redirection": redirection directly inferred from the
  url without needing to make any HTTP request.
. "domain_name": TLD-aware domain name of the url.
. "hostname": full hostname of the url.
. "normalized_hostname": normalized hostname, i.e. stripped of "www",
  "m" or some language subdomains etc., of the url.
. "shortened": whether the url is probably shortened or
  not (bit.ly, t.co etc.).
. "typo": whether the url probably contains typo or not
  (such as inclusive language in french : curieux.se etc.).
. "homepage": whether the given url looks like a website's
  homepage.
. "should_resolve": whether the given url looks like something
  we should resolve, i.e. shortened url.

columns being added with --facebook:

. "facebook_type": the type of Facebook resource symbolized by the
  parsed url (post, video etc.).
. "facebook_id": Facebook resource id.
. "facebook_full_id": Facebook full resource id.
. "facebook_handle": Facebook handle for people, pages etc.
. "facebook_normalized_url": normalized Facebook url.

columns being added with --youtube:

. "youtube_type": YouTube resource type (video, channel etc.).
. "youtube_id": YouTube resource id.
. "youtube_name": YouTube resource name.

columns being added with --twitter:

. "twitter_type": Twitter resource type (user or tweet).
. "twitter_user_screen_name": Twitter user's screen name.
. "tweet_id": id of tweet.

examples:

. Creating a report about a file's urls:
    $ minet url-parse url posts.csv > report.csv

. Keeping only selected columns from the input file:
    $ minet url-parse url posts.csv -s id,url,title > report.csv

. Multiple urls joined by separator:
    $ minet url-parse urls posts.csv --separator "|" > report.csv

. Parsing Facebook urls:
    $ minet url-parse url fbposts.csv --facebook > report.csv

. Parsing YouTube urls:
    $ minet url-parse url ytvideos.csv --youtube > report.csv

. Parsing Twitter urls:
    $ minet url-parse url tweets.csv --twitter > report.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## BuzzSumo

```
usage: minet buzzsumo [-h] [-t TOKEN] [--rcfile RCFILE]
                      {limit,domain,domain-summary} ...

Minet Buzzsumo Command
======================

Gather data from the BuzzSumo APIs easily and efficiently.

optional arguments:
  -t TOKEN, --token TOKEN       BuzzSumo API token. Can also be configured in a
                                .minetrc file as "buzzsumo.token" or read from
                                the MINET_BUZZSUMO_TOKEN env variable.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

subcommands:
  {limit,domain,domain-summary}
                                Subcommand to use.
```

<h3 id="buzzsumo-limit">limit</h3>

```
usage: minet buzzsumo limit [-h] [-t TOKEN] [--rcfile RCFILE] [-o OUTPUT]

Minet Buzzsumo Limit Command
============================

Call BuzzSumo for a given request and return the remaining number
of calls for this month contained in the request's headers.

optional arguments:
  -t TOKEN, --token TOKEN     BuzzSumo API token. Can also be configured in a
                              .minetrc file as "buzzsumo.token" or read from the
                              MINET_BUZZSUMO_TOKEN env variable.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Returning the remaining number of calls for this month:
    $ minet bz limit --token YOUR_TOKEN
```

<h3 id="buzzsumo-domain-summary">domain-summary</h3>

```
usage: minet buzzsumo domain-summary [-h] [-t TOKEN] [--rcfile RCFILE]
                                     --begin-date BEGIN_DATE --end-date END_DATE
                                     [-i INPUT] [-s SELECT] [-o OUTPUT]
                                     value_or_column_name

Minet Buzzsumo Domain Summary Command
=====================================

Gather information about the quantity of articles crawled by BuzzSumo for certain domain names and a given period.

Inform the user about the number of calls (corresponding to the number of pages) needed to request BuzzSumo about those domain names.

positional arguments:
  value_or_column_name        Single domain name to process or name of the CSV
                              column containing domain names when using
                              -i/--input.

optional arguments:
  --begin-date BEGIN_DATE     The date you wish to fetch articles from. UTC date
                              should have the following format : YYYY-MM-DD
  --end-date END_DATE         The date you wish to fetch articles to. UTC date
                              should have the following format : YYYY-MM-DD
  -t TOKEN, --token TOKEN     BuzzSumo API token. Can also be configured in a
                              .minetrc file as "buzzsumo.token" or read from the
                              MINET_BUZZSUMO_TOKEN env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the domain names you want
                              to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Returning the number of articles and pages found in BuzzSumo for one domain name:
    $ minet bz domain-summary 'nytimes.com' --begin-date 2019-01-01 --end-date 2019-03-01 --token YOUR_TOKEN

. Returning the number of articles and pages found in BuzzSumo for a list of domain names in a CSV:
    $ minet bz domain-summary domain_name domain_names.csv --begin-date 2020-01-01 --end-date 2021-06-15 --token YOUR_TOKEN  > domain_name_summary.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="buzzsumo-domain">domain</h3>

```
usage: minet buzzsumo domain [-h] [-t TOKEN] [--rcfile RCFILE] --begin-date
                             BEGIN_DATE --end-date END_DATE [-i INPUT]
                             [-s SELECT] [-o OUTPUT]
                             value_or_column_name

Minet Buzzsumo Domain Command
=============================

Gather social media information about all the articles crawled by BuzzSumo for one or a list of domain names and over a given period.

The link to the official documentation: https://developers.buzzsumo.com/reference/articles.

positional arguments:
  value_or_column_name        Single domain name to process or name of the CSV
                              column containing domain names when using
                              -i/--input.

optional arguments:
  --begin-date BEGIN_DATE     The date you wish to fetch articles from. UTC date
                              should have the following format : YYYY-MM-DD
  --end-date END_DATE         The date you wish to fetch articles to. UTC date
                              should have the following format : YYYY-MM-DD
  -t TOKEN, --token TOKEN     BuzzSumo API token. Can also be configured in a
                              .minetrc file as "buzzsumo.token" or read from the
                              MINET_BUZZSUMO_TOKEN env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the domain names you want
                              to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Returning social media information for one domain name:
    $ minet bz domain 'trump-feed.com' --begin-date 2021-01-01 --end-date 2021-06-30 --token YOUR_TOKEN > trump_feed_articles.csv

. Returning social media information for a list of domain names in a CSV:
    $ minet bz domain domain_name domain_names.csv --select domain_name --begin-date 2019-01-01 --end-date 2020-12-31 --token YOUR_TOKEN > domain_name_articles.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## CrowdTangle

```
usage: minet crowdtangle [-h] [--rate-limit RATE_LIMIT] [--rcfile RCFILE]
                         [-t TOKEN]
                         {leaderboard,lists,posts-by-id,posts,search,summary}
                         ...

Minet Crowdtangle Command
=========================

Gather data from the CrowdTangle APIs easily and efficiently.

optional arguments:
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to 6. Rcfile key: crowdtangle.rate_limit. Can
                                also be configured in a .minetrc file as
                                "crowdtangle.rate_limit" or read from the
                                MINET_CROWDTANGLE_RATE_LIMIT env variable.
  -t TOKEN, --token TOKEN       CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

subcommands:
  {leaderboard,lists,posts-by-id,posts,search,summary}
                                Subcommand to use.
```

### leaderboard

```
usage: minet crowdtangle leaderboard [-h] [--rate-limit RATE_LIMIT]
                                     [--rcfile RCFILE] [-t TOKEN]
                                     [--no-breakdown] [-f {csv,jsonl}]
                                     [-l LIMIT] [--list-id LIST_ID]
                                     [--start-date START_DATE] [-o OUTPUT]

Minet CrowdTangle Leaderboard Command
=====================================

Gather information and aggregated stats about pages and groups of the designated dashboard (indicated by a given token).

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Leaderboard.

optional arguments:
  --no-breakdown                Whether to skip statistics breakdown by post
                                type in the CSV output.
  -f {csv,jsonl}, --format {csv,jsonl}
                                Output format. Defaults to `csv`.
  -l LIMIT, --limit LIMIT       Maximum number of accounts to retrieve. Will
                                fetch every account by default.
  --list-id LIST_ID             Optional list id from which to retrieve
                                accounts.
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to 6. Rcfile key: crowdtangle.rate_limit. Can
                                also be configured in a .minetrc file as
                                "crowdtangle.rate_limit" or read from the
                                MINET_CROWDTANGLE_RATE_LIMIT env variable.
  --start-date START_DATE       The earliest date at which to start aggregating
                                statistics (UTC!). You can pass just a year or a
                                year-month for convenience.
  -t TOKEN, --token TOKEN       CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Fetching accounts statistics for every account in your dashboard:
    $ minet ct leaderboard --token YOUR_TOKEN > accounts-stats.csv
```

### lists

```
usage: minet crowdtangle lists [-h] [--rate-limit RATE_LIMIT] [--rcfile RCFILE]
                               [-t TOKEN] [-o OUTPUT]

Minet CrowdTangle Lists Command
===============================

Retrieve the lists from a CrowdTangle dashboard (indicated by a given token).

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Lists.

optional arguments:
  --rate-limit RATE_LIMIT     Authorized number of hits by minutes. Defaults to
                              6. Rcfile key: crowdtangle.rate_limit. Can also be
                              configured in a .minetrc file as
                              "crowdtangle.rate_limit" or read from the
                              MINET_CROWDTANGLE_RATE_LIMIT env variable.
  -t TOKEN, --token TOKEN     CrowdTangle dashboard API token. Rcfile key:
                              crowdtangle.token. Can also be configured in a
                              .minetrc file as "crowdtangle.token" or read from
                              the MINET_CROWDTANGLE_TOKEN env variable.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Fetching a dashboard's lists:
    $ minet ct lists --token YOUR_TOKEN > lists.csv
```

### posts-by-id

```
usage: minet crowdtangle posts-by-id [-h] [--rate-limit RATE_LIMIT]
                                     [--rcfile RCFILE] [-t TOKEN] [-i INPUT]
                                     [-s SELECT] [--total TOTAL] [--resume]
                                     [-o OUTPUT]
                                     value_or_column_name

Minet CrowdTangle Post By Id Command
====================================

Retrieve metadata about batches of posts using Crowdtangle's API.

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Posts#get-postid.

positional arguments:
  value_or_column_name        Single URL or id to process or name of the CSV
                              column containing URLs or ids when using
                              -i/--input.

optional arguments:
  --rate-limit RATE_LIMIT     Authorized number of hits by minutes. Defaults to
                              6. Rcfile key: crowdtangle.rate_limit. Can also be
                              configured in a .minetrc file as
                              "crowdtangle.rate_limit" or read from the
                              MINET_CROWDTANGLE_RATE_LIMIT env variable.
  -t TOKEN, --token TOKEN     CrowdTangle dashboard API token. Rcfile key:
                              crowdtangle.token. Can also be configured in a
                              .minetrc file as "crowdtangle.token" or read from
                              the MINET_CROWDTANGLE_TOKEN env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the URLs or ids you want
                              to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --resume                    Whether to resume from an aborted collection. Need
                              -o to be set.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Retrieving information about a batch of posts:
    $ minet ct posts-by-id post-url posts.csv --token YOUR_TOKEN > metadata.csv

. Retrieving information about a single post:
    $ minet ct posts-by-id 1784333048289665 --token YOUR_TOKEN

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### posts

```
usage: minet crowdtangle posts [-h] [--rate-limit RATE_LIMIT] [--rcfile RCFILE]
                               [-t TOKEN] [--chunk-size CHUNK_SIZE]
                               [--end-date END_DATE] [-f {csv,jsonl}]
                               [--language LANGUAGE] [-l LIMIT]
                               [--list-ids LIST_IDS]
                               [--sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}]
                               [--start-date START_DATE] [--resume] [-o OUTPUT]

Minet CrowdTangle Posts Command
===============================

Gather post data from the designated dashboard (indicated by a given token).

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Posts.

optional arguments:
  --chunk-size CHUNK_SIZE       When sorting by date (default), the number of
                                items to retrieve before shifting the inital
                                query to circumvent the APIs limitations.
                                Defaults to 500.
  --end-date END_DATE           The latest date at which a post could be posted
                                (UTC!). You can pass just a year or a year-month
                                for convenience.
  -f {csv,jsonl}, --format {csv,jsonl}
                                Output format. Defaults to `csv`.
  --language LANGUAGE           Language of posts to retrieve.
  -l LIMIT, --limit LIMIT       Maximum number of posts to retrieve. Will fetch
                                every post by default.
  --list-ids LIST_IDS           Ids of the lists from which to retrieve posts,
                                separated by commas.
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to 6. Rcfile key: crowdtangle.rate_limit. Can
                                also be configured in a .minetrc file as
                                "crowdtangle.rate_limit" or read from the
                                MINET_CROWDTANGLE_RATE_LIMIT env variable.
  --sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}
                                The order in which to retrieve posts. Defaults
                                to `date`.
  --start-date START_DATE       The earliest date at which a post could be
                                posted (UTC!). You can pass just a year or a
                                year-month for convenience. Defaults to `2010`.
  -t TOKEN, --token TOKEN       CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Fetching the 500 most latest posts from a dashboard (a start date must be precised):
    $ minet ct posts --token YOUR_TOKEN --limit 500 --start-date 2021-01-01 > latest-posts.csv

. If your collection is interrupted, it can be restarted from the last data collected with the --resume option:
    $ minet ct posts --token YOUR_TOKEN --limit 500 --start-date 2021-01-01 --resume --output latest-posts.csv

. Fetching all the posts from a specific list of groups or pages:
    $ minet ct posts --token YOUR_TOKEN --start-date 2021-01-01 --list-ids YOUR_LIST_ID > posts_from_one_list.csv

To know the different list ids associated with your dashboard:
    $ minet ct lists --token YOUR_TOKEN
```

<h3 id="ct-search">search</h3>

```
usage: minet crowdtangle search [-h] [--rate-limit RATE_LIMIT] [--rcfile RCFILE]
                                [-t TOKEN] [--and AND] [--chunk-size CHUNK_SIZE]
                                [--end-date END_DATE] [-f {csv,jsonl}]
                                [--in-list-ids IN_LIST_IDS]
                                [--language LANGUAGE] [-l LIMIT]
                                [--not-in-title] [--offset OFFSET]
                                [-p PLATFORMS]
                                [--search-field {account_name_only,image_text_only,include_query_strings,text_fields_and_image_text,text_fields_only}]
                                [--sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}]
                                [--start-date START_DATE] [--types TYPES]
                                [-o OUTPUT]
                                terms

Minet CrowdTangle Search Command
================================

Search posts on the whole CrowdTangle platform.

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Search.

positional arguments:
  terms                         The search query term or terms.

optional arguments:
  --and AND                     AND clause to add to the query terms.
  --chunk-size CHUNK_SIZE       When sorting by date (default), the number of
                                items to retrieve before shifting the inital
                                query to circumvent the APIs limitations.
                                Defaults to 500.
  --end-date END_DATE           The latest date at which a post could be posted
                                (UTC!). You can pass just a year or a year-month
                                for convenience.
  -f {csv,jsonl}, --format {csv,jsonl}
                                Output format. Defaults to `csv`.
  --in-list-ids IN_LIST_IDS     Ids of the lists in which to search, separated
                                by commas.
  --language LANGUAGE           Language ISO code like "fr" or "zh-CN".
  -l LIMIT, --limit LIMIT       Maximum number of posts to retrieve. Will fetch
                                every post by default.
  --not-in-title                Whether to search terms in account titles also.
  --offset OFFSET               Count offset.
  -p PLATFORMS, --platforms PLATFORMS
                                The platforms from which to retrieve links
                                (facebook, instagram, or reddit). This value can
                                be comma-separated.
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to 6. Rcfile key: crowdtangle.rate_limit. Can
                                also be configured in a .minetrc file as
                                "crowdtangle.rate_limit" or read from the
                                MINET_CROWDTANGLE_RATE_LIMIT env variable.
  --search-field {account_name_only,image_text_only,include_query_strings,text_fields_and_image_text,text_fields_only}
                                In what to search the query. Defaults to
                                `text_fields_and_image_text`.
  --sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}
                                The order in which to retrieve posts. Defaults
                                to `date`.
  --start-date START_DATE       The earliest date at which a post could be
                                posted (UTC!). You can pass just a year or a
                                year-month for convenience. Defaults to `2010`.
  -t TOKEN, --token TOKEN       CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
  --types TYPES                 Types of post to include, separated by comma.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Fetching all the 2021 posts containing the words 'acetylsalicylic acid':
    $ minet ct search 'acetylsalicylic acid' --start-date 2021-01-01 --token YOUR_TOKEN > posts.csv
```

### summary

```
usage: minet crowdtangle summary [-h] [--rate-limit RATE_LIMIT]
                                 [--rcfile RCFILE] [-t TOKEN] [-p PLATFORMS]
                                 [--posts POSTS]
                                 [--sort-by {date,subscriber_count,total_interactions}]
                                 --start-date START_DATE [-i INPUT] [-s SELECT]
                                 [--total TOTAL] [-o OUTPUT]
                                 value_or_column_name

Minet CrowdTangle Link Summary Command
======================================

Retrieve aggregated statistics about link sharing on the Crowdtangle API and by platform.

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Links.

positional arguments:
  value_or_column_name          Single URL to process or name of the CSV column
                                containing URLs when using -i/--input.

optional arguments:
  -p PLATFORMS, --platforms PLATFORMS
                                The platforms from which to retrieve links
                                (facebook, instagram, or reddit). This value can
                                be comma-separated.
  --posts POSTS                 Path to a file containing the retrieved posts.
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to 6. Rcfile key: crowdtangle.rate_limit. Can
                                also be configured in a .minetrc file as
                                "crowdtangle.rate_limit" or read from the
                                MINET_CROWDTANGLE_RATE_LIMIT env variable.
  --sort-by {date,subscriber_count,total_interactions}
                                How to sort retrieved posts. Defaults to `date`.
  --start-date START_DATE       The earliest date at which a post could be
                                posted (UTC!). You can pass just a year or a
                                year-month for convenience. Defaults to `2010`.
  -t TOKEN, --token TOKEN       CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the URLs you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Computing a summary of aggregated stats for urls contained in a CSV row:
    $ minet ct summary url urls.csv --token YOUR_TOKEN --start-date 2019-01-01 > summary.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## Facebook

```
usage: minet facebook [-h]
                      {comments,post-authors,post-stats,post,posts,url-likes}
                      ...

Minet Facebook Command
======================

Collect data from Facebook.

optional arguments:
  -h, --help                    show this help message and exit

subcommands:
  {comments,post-authors,post-stats,post,posts,url-likes}
                                Subcommand to use.
```

<h3 id="facebook-comments">comments</h3>

```
usage: minet facebook comments [-h] [-c COOKIE] [--rcfile RCFILE]
                               [--throttle THROTTLE] [-i INPUT] [-s SELECT]
                               [-o OUTPUT]
                               value_or_column_name

Minet Facebook Comments Command
===============================

Scrape a Facebook post's comments.

This requires to be logged in to a Facebook account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

positional arguments:
  value_or_column_name        Single post url to process or name of the CSV
                              column containing post urls when using -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "facebook.cookie" or read from the
                              MINET_FACEBOOK_COOKIE env variable.
  --throttle THROTTLE         Throttling time, in seconds, to wait between each
                              request.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the post urls you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Scraping a post's comments:
    $ minet fb comments https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

. Grabbing cookies from chrome:
    $ minet fb comments -c chrome https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

. Scraping comments from multiple posts listed in a CSV file:
    $ minet fb comments post_url posts.csv > comments.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="facebook-post">post</h3>

```
usage: minet facebook post [-h] [-c COOKIE] [--rcfile RCFILE]
                           [--throttle THROTTLE] [-i INPUT] [-s SELECT]
                           [-o OUTPUT]
                           value_or_column_name

Minet Facebook Post Command
===========================

Scrape Facebook post.

This requires to be logged in to a Facebook account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

You must set your account language to English (US) for the
command to work.

Note that, by default, Facebook will translate post text
when they are not written in a language whitelisted here:
https://www.facebook.com/settings/?tab=language

In this case, minet will output both the original text and
the translated one. But be aware that original text may be
truncated, so you might want to edit your Facebook settings
using the url above to make sure text won't be translated
for posts you are interested in.

Of course, the CLI will warn you when translated text is
found so you can choose to edit your settings early as
as possible.

Finally, some post text is always truncated on Facebook
when displayed in lists. This text is not yet entirely
scraped by minet at this time.

positional arguments:
  value_or_column_name        Single post url to process or name of the CSV
                              column containing post urls when using -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "facebook.cookie" or read from the
                              MINET_FACEBOOK_COOKIE env variable.
  --throttle THROTTLE         Throttling time, in seconds, to wait between each
                              request.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the post urls you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Scraping a post:
    $ minet fb post https://m.facebook.com/watch/?v=448540820705115 > post.csv

. Grabbing cookies from chrome:
    $ minet fb posts -c chrome https://m.facebook.com/watch/?v=448540820705115 > post.csv

. Scraping post from multiple urls listed in a CSV file:
    $ minet fb post url urls.csv > post.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="facebook-posts">posts</h3>

```
usage: minet facebook posts [-h] [-c COOKIE] [--rcfile RCFILE]
                            [--throttle THROTTLE] [-i INPUT] [-s SELECT]
                            [-o OUTPUT]
                            value_or_column_name

Minet Facebook Posts Command
============================

Scrape Facebook posts.

This requires to be logged in to a Facebook account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

Scraping posts currently only works for Facebook groups.

Note that, by default, Facebook will translate post text
when they are not written in a language whitelisted here:
https://www.facebook.com/settings/?tab=language

In this case, minet will output both the original text and
the translated one. But be aware that original text may be
truncated, so you might want to edit your Facebook settings
using the url above to make sure text won't be translated
for posts you are interested in.

Of course, the CLI will warn you when translated text is
found so you can choose to edit your settings early as
as possible.

Finally, some post text is always truncated on Facebook
when displayed in lists. This text is not yet entirely
scraped by minet at this time.

positional arguments:
  value_or_column_name        Single group url to process or name of the CSV
                              column containing group urls when using
                              -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "facebook.cookie" or read from the
                              MINET_FACEBOOK_COOKIE env variable.
  --throttle THROTTLE         Throttling time, in seconds, to wait between each
                              request.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the group urls you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Scraping a group's posts:
    $ minet fb posts https://www.facebook.com/groups/444175323127747 > posts.csv

. Grabbing cookies from chrome:
    $ minet fb posts -c chrome https://www.facebook.com/groups/444175323127747 > posts.csv

. Scraping posts from multiple groups listed in a CSV file:
    $ minet fb posts group_url groups.csv > posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="facebook-post-authors">post-authors</h3>

```
usage: minet facebook post-authors [-h] [-c COOKIE] [--rcfile RCFILE]
                                   [--throttle THROTTLE] [-i INPUT] [-s SELECT]
                                   [--total TOTAL] [-o OUTPUT]
                                   value_or_column_name

Minet Facebook Post Authors Command
===================================

Retrieve the author of the given Facebook posts.

Note that it is only relevant for group posts since
only administrators can post something on pages.

positional arguments:
  value_or_column_name        Single post to process or name of the CSV column
                              containing posts when using -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "facebook.cookie" or read from the
                              MINET_FACEBOOK_COOKIE env variable.
  --throttle THROTTLE         Throttling time, in seconds, to wait between each
                              request.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the posts you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

examples:

. Fetching authors of a series of posts in a CSV file:
    $ minet fb post-authors post_url fb-posts.csv > authors.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="facebook-url-likes">url-likes</h3>

```
usage: minet facebook url-likes [-h] [-i INPUT] [-s SELECT] [--total TOTAL]
                                [-o OUTPUT]
                                value_or_column_name

Minet Facebook Url Likes Command
================================

Retrieve the approximate number of "likes" (actually an aggregated engagement metric)
that a url got on Facebook. The command can also be used with a list of urls stored in a CSV file.
This number is found by scraping Facebook's share button, which only gives a
rough estimation of the real engagement metric: "Share 45K" for example.

Note that this number does not actually only correspond to the number of
likes or shares, but it is rather the sum of like, love, ahah, angry, etc.
reactions plus the number of comments and shares that the URL got on Facebook
(here is the official documentation: https://developers.facebook.com/docs/plugins/faqs
explaining "What makes up the number shown next to my Share button?").

positional arguments:
  value_or_column_name        Single url to process or name of the CSV column
                              containing urls when using -i/--input.

optional arguments:
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the urls you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

example:
. Retrieving the "like" number for one url:
    $ minet fb url-likes "www.example-url.com" > url_like.csv

. Retrieving the "like" number for the urls listed in a CSV file:
    $ minet fb url-likes url url.csv > url_likes.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## Google

```
usage: minet google [-h] {sheets} ...

Minet Google Command
====================

Collect data from Google.

optional arguments:
  -h, --help  show this help message and exit

subcommands:
  {sheets}    Subcommand to use.
```

<h3 id="google-sheets">sheets</h3>

```
usage: minet google sheets [-h] [-a AUTHUSER] [-c COOKIE] [-o OUTPUT] url

Minet Google Sheets Command
===========================

Grab the given google spreadsheet as a CSV file from
its url, its sharing url or id.

It can access public spreadsheets without issues, but to
you will need to tell the command how to retrieve Google
drive authentication cookies to also be able to access
private ones.

Also note that by default, the command will try to access
your spreadsheet using your first 4 connected Google
accounts.

If you have more connected accounts or know beforehand
to which account some spreadsheets are tied to, be sure
to give --authuser.

positional arguments:
  url                           Url, sharing url or id of the spreadsheet to
                                export.

optional arguments:
  -a AUTHUSER, --authuser AUTHUSER
                                Connected google account number to use.
  -c COOKIE, --cookie COOKIE    Google Drive cookie or browser from which to
                                extract it (supports "firefox", "chrome",
                                "chromium", "opera" and "edge").
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  -h, --help                    show this help message and exit

examples:

. Exporting from the spreadsheet id:
    $ minet google sheets 1QXQ1yaNYrVUlMt6LQ4jrLGt_PvZI9goozYiBTgaC4RI > file.csv

. Using your Firefox authentication cookies:
    $ minet google sheets --cookie firefox 1QXQ1yaNYrVUlMt6LQ4jrLGt_PvZI9goozYiBTgaC4RI > file.csv
```

## Hyphe

<h3 id="hyphe-declare">declare</h3>

```
usage: minet hyphe declare [-h] [--password PASSWORD] [--total TOTAL]
                           [-o OUTPUT]
                           url corpus webentities

Minet Hyphe Declare Command
===========================

Command that can be used to declare series of webentities
in a corpus.

It is ideal to start or restart a corpus using the same exact
webentity declarations as another one.

positional arguments:
  url                         Url of the Hyphe API.
  corpus                      Id of the corpus.
  webentities                 CSV file of webentities (exported from Hyphe).

optional arguments:
  --password PASSWORD         The corpus's password if required.
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:

. Declaring webentities from a Hyphe export:
    $ minet hyphe declare http://myhyphe.com/api/ target-corpus export.csv
```

<h3 id="hyphe-destroy">destroy</h3>

```
usage: minet hyphe destroy [-h] [--password PASSWORD] [-o OUTPUT] url corpus

Minet Hyphe Destroy Command
===========================

Command that can be used to destroy a corpus entirely.

positional arguments:
  url                         Url of the Hyphe API.
  corpus                      Id of the corpus.

optional arguments:
  --password PASSWORD         The corpus's password if required.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:

. Destroying a corpus:
    $ minet hyphe destroy http://myhyphe.com/api/ my-corpus
```

<h3 id="hyphe-dump">dump</h3>

```
usage: minet hyphe dump [-h] [-O OUTPUT_DIR] [--body] [--statuses STATUSES]
                        [--password PASSWORD] [-o OUTPUT]
                        url corpus

Minet Hyphe Dump Command
========================

Command dumping page-level information from a given
Hyphe corpus.

positional arguments:
  url                           Url of the Hyphe API.
  corpus                        Id of the corpus.

optional arguments:
  --body                        Whether to download pages body.
  -O OUTPUT_DIR, --output-dir OUTPUT_DIR
                                Output directory for dumped files. Will default
                                to some name based on corpus name.
  --password PASSWORD           The corpus's password if required.
  --statuses STATUSES           Webentity statuses to dump, separated by comma.
                                Possible statuses being "IN", "OUT", "UNDECIDED"
                                and "DISCOVERED".
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  -h, --help                    show this help message and exit

examples:

. Dumping a corpus into the ./corpus directory:
    $ minet hyphe dump http://myhyphe.com/api/ corpus-name -O corpus
```

<h3 id="hyphe-reset">reset</h3>

```
usage: minet hyphe reset [-h] [--password PASSWORD] [-o OUTPUT] url corpus

Minet Hyphe Reset Command
=========================

Command that can be used to reset a corpus entirely.

positional arguments:
  url                         Url of the Hyphe API.
  corpus                      Id of the corpus.

optional arguments:
  --password PASSWORD         The corpus's password if required.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:

. Resetting a corpus:
    $ minet hyphe reset http://myhyphe.com/api/ my-corpus
```

<h3 id="hyphe-tag">tag</h3>

```
usage: minet hyphe tag [-h] [--separator SEPARATOR] [--password PASSWORD]
                       [--total TOTAL] [-o OUTPUT]
                       url corpus webentity_id_column tag_columns data

Minet Hyphe Tag Command
=======================

Command that can be used to tag webentities in batch using
metadata recorded in a CSV file.

positional arguments:
  url                         Url of the Hyphe API.
  corpus                      Id of the corpus.
  webentity_id_column         Column of the CSV file containing the webentity
                              ids.
  tag_columns                 Columns, separated by comma, to use as tags.
  data                        CSV file of webentities (exported from Hyphe).

optional arguments:
  --password PASSWORD         The corpus's password if required.
  --separator SEPARATOR       Separator use to split multiple tag values in the
                              same column. Defaults to "|".
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:

. Tag webentities from two columns of CSV file:
    $ minet hyphe tag http://myhyphe.com/api/ my-corpus webentity_id type,creator metadata.csv
```

## Instagram

```
usage: minet instagram [-h] [-c COOKIE] [--rcfile RCFILE]
                       {hashtag,user-followers,user-following,user-infos,user-posts}
                       ...

Minet Instagram Command
=======================

Gather data from Instagram.

optional arguments:
  -c COOKIE, --cookie COOKIE    Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to "firefox". Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

subcommands:
  {hashtag,user-followers,user-following,user-infos,user-posts}
                                Subcommand to use.
```

### hashtag

```
usage: minet instagram hashtag [-h] [-c COOKIE] [--rcfile RCFILE] [-l LIMIT]
                               [-i INPUT] [-s SELECT] [--total TOTAL]
                               [-o OUTPUT]
                               value_or_column_name

Instagram hashtag
=================

Scrape Instagram posts with a given hashtag.

This requires to be logged in to an Instagram account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

display_url is not the media url, but a thumbnail of the post.
There is no way with this command to get the media urls.

positional arguments:
  value_or_column_name        Single hashtag to process or name of the CSV
                              column containing hashtags when using -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "instagram.cookie" or read from the
                              MINET_INSTAGRAM_COOKIE env variable.
  -l LIMIT, --limit LIMIT     Maximum number of posts to retrieve per hashtag.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the hashtags you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Searching posts with the hashtag paris:
    $ minet instagram hashtag paris > paris_posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### user-followers

```
usage: minet instagram user-followers [-h] [-c COOKIE] [--rcfile RCFILE]
                                      [-l LIMIT] [-i INPUT] [-s SELECT]
                                      [-o OUTPUT]
                                      value_or_column_name

Instagram User Followers Command
================================

Scrape Instagram followers with a given username or user url.
On verified accounts, you may be unable to get all of them.

This requires to be logged in to an Instagram account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

Beware, instagram only provides temporary links, not permalinks,
for profile picture urls retrieved as the "profile_pic_url" in
the result. Be sure to download them fast if you need them (you can
use the `minet fetch` command for that, and won't need to use cookies).

positional arguments:
  value_or_column_name        Single username or user url to process or name of
                              the CSV column containing usernames or user urls
                              when using -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "instagram.cookie" or read from the
                              MINET_INSTAGRAM_COOKIE env variable.
  -l LIMIT, --limit LIMIT     Maximum number of followers to retrieve per user.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the usernames or user urls
                              you want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Searching followers with the username banksrepeta:
    $ minet instagram user-followers banksrepeta > banksrepeta_followers.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### user-following

```
usage: minet instagram user-following [-h] [-c COOKIE] [--rcfile RCFILE]
                                      [-l LIMIT] [-i INPUT] [-s SELECT]
                                      [-o OUTPUT]
                                      value_or_column_name

Instagram User Following Command
================================

Scrape Instagram accounts followed with a given username.

This requires to be logged in to an Instagram account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

Beware, instagram only provides temporary links, not permalinks,
for profile picture urls retrieved as the "profile_pic_url" in
the result. Be sure to download them fast if you need them (you can
use the `minet fetch` command for that, and won't need to use cookies).

positional arguments:
  value_or_column_name        Single username or user url to process or name of
                              the CSV column containing usernames or user urls
                              when using -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "instagram.cookie" or read from the
                              MINET_INSTAGRAM_COOKIE env variable.
  -l LIMIT, --limit LIMIT     Maximum number of accounts to retrieve per user.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the usernames or user urls
                              you want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Searching accounts followed with the username paramountplus:
    $ minet instagram user-following paramountplus > paramountplus_following.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### user-infos

```
usage: minet instagram user-infos [-h] [-c COOKIE] [--rcfile RCFILE] [-i INPUT]
                                  [-s SELECT] [-o OUTPUT]
                                  value_or_column_name

Instagram user-infos
====================

Scrape Instagram infos with a given username or user url.

This requires to be logged in to an Instagram account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

Beware, instagram only provides temporary links, not permalinks,
for profile picture urls retrieved as the "profile_pic_url_hd" in
the result. Be sure to download them fast if you need them (you can
use the `minet fetch` command for that, and won't need to use cookies).

positional arguments:
  value_or_column_name        Single username or user url to process or name of
                              the CSV column containing usernames or user urls
                              when using -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "instagram.cookie" or read from the
                              MINET_INSTAGRAM_COOKIE env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the usernames or user urls
                              you want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Searching infos with the username banksrepeta:
    $ minet instagram user-infos banksrepeta > banksrepeta_infos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### user-posts

```
usage: minet instagram user-posts [-h] [-c COOKIE] [--rcfile RCFILE] [-l LIMIT]
                                  [-i INPUT] [-s SELECT] [-o OUTPUT]
                                  value_or_column_name

Instagram User Posts Command
============================

Scrape Instagram posts with a given username or user url.

This requires to be logged in to an Instagram account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

The urls in the medias_url column have a limited life time.
It is not the case for the url in main_thumbnail_url, which
corresponds to the first image (the video cover if the first
media is a video). Be sure to download them fast if you need
them (you can use the `minet fetch` command for that, and
won't need to use cookies).

positional arguments:
  value_or_column_name        Single username or user url to process or name of
                              the CSV column containing usernames or user urls
                              when using -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "instagram.cookie" or read from the
                              MINET_INSTAGRAM_COOKIE env variable.
  -l LIMIT, --limit LIMIT     Maximum number of posts to retrieve per user.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the usernames or user urls
                              you want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Searching posts from the account paramountplus:
    $ minet instagram user-posts paramountplus > paramountplus_posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## Mediacloud

<h3 id="mc-medias">medias</h3>

```
usage: minet mediacloud medias [-h] [-t TOKEN] [--rcfile RCFILE] [--feeds FEEDS]
                               [-i INPUT] [-s SELECT] [--total TOTAL]
                               [-o OUTPUT]
                               value_or_column_name

Minet Mediacloud Medias Command
===============================

Retrieve metadata about a list of Mediacloud medias.

positional arguments:
  value_or_column_name        Single Mediacloud media id to process or name of
                              the CSV column containing Mediacloud media ids
                              when using -i/--input.

optional arguments:
  --feeds FEEDS               If given, path of the CSV file listing media RSS
                              feeds.
  -t TOKEN, --token TOKEN     Mediacloud API token (also called "key"
                              sometimes). Can also be configured in a .minetrc
                              file as "mediacloud.token" or read from the
                              MINET_MEDIACLOUD_TOKEN env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the Mediacloud media ids
                              you want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="mc-search">search</h3>

```
usage: minet mediacloud search [-h] [-t TOKEN] [--rcfile RCFILE]
                               [-c COLLECTIONS] [--filter-query FILTER_QUERY]
                               [-m MEDIAS] [--publish-day PUBLISH_DAY]
                               [--publish-month PUBLISH_MONTH]
                               [--publish-year PUBLISH_YEAR] [--skip-count]
                               [-o OUTPUT]
                               query

Minet Mediacloud Search Command
===============================

Search stories on the Mediacloud platform.
To learn how to compose more relevant queries, check out this guide:
https://mediacloud.org/support/query-guide

positional arguments:
  query                         Search query.

optional arguments:
  -c COLLECTIONS, --collections COLLECTIONS
                                List of collection ids to search, separated by
                                commas.
  --filter-query FILTER_QUERY   Solr filter query `fq` to use. Can be used to
                                optimize some parts of the query.
  -m MEDIAS, --medias MEDIAS    List of media ids to search, separated by
                                commas.
  --publish-day PUBLISH_DAY     Only search stories published on provided day
                                (iso format, e.g. "2018-03-24").
  --publish-month PUBLISH_MONTH
                                Only search stories published on provided month
                                (iso format, e.g. "2018-03").
  --publish-year PUBLISH_YEAR   Only search stories published on provided year
                                (iso format, e.g. "2018").
  --skip-count                  Whether to skip the first API call counting the
                                number of posts for the progress bar.
  -t TOKEN, --token TOKEN       Mediacloud API token (also called "key"
                                sometimes). Can also be configured in a .minetrc
                                file as "mediacloud.token" or read from the
                                MINET_MEDIACLOUD_TOKEN env variable.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit
```

### topic

#### stories

```
usage: minet mediacloud topic stories [-h] [-t TOKEN] [--rcfile RCFILE]
                                      [--media-id MEDIA_ID]
                                      [--from-media-id FROM_MEDIA_ID]
                                      topic_id

Minet Mediacloud Topic Stories Command
======================================

Retrieves the list of stories from a mediacloud topic.

positional arguments:
  topic_id                      Id of the topic.

optional arguments:
  --from-media-id FROM_MEDIA_ID
                                Return only stories that are linked from stories
                                in the given media_id.
  --media-id MEDIA_ID           Return only stories belonging to the given
                                media_ids.
  -t TOKEN, --token TOKEN       Mediacloud API token (also called "key"
                                sometimes). Can also be configured in a .minetrc
                                file as "mediacloud.token" or read from the
                                MINET_MEDIACLOUD_TOKEN env variable.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit
```

## Telegram

### channel-infos

```
usage: minet telegram channel-infos [-h] [--throttle THROTTLE] [-i INPUT]
                                    [-s SELECT] [-o OUTPUT]
                                    value_or_column_name

Minet Telegram Channel-Infos Command
====================================

Scrape a Telegram channel's infos.

positional arguments:
  value_or_column_name        Single channel name / url to process or name of
                              the CSV column containing channel names / urls
                              when using -i/--input.

optional arguments:
  --throttle THROTTLE         Throttling time, in seconds, to wait between each
                              request.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the channel names / urls
                              you want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:
. Scraping a channel's infos:
    $ minet telegram channel-infos nytimes > infos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### channel-messages

```
usage: minet telegram channel-messages [-h] [--throttle THROTTLE] [-i INPUT]
                                       [-s SELECT] [-o OUTPUT]
                                       value_or_column_name

Minet Telegram Channel-Messages Command
=======================================

Scrape Telegram channel messages.

positional arguments:
  value_or_column_name        Single channel name / url to process or name of
                              the CSV column containing channel names / urls
                              when using -i/--input.

optional arguments:
  --throttle THROTTLE         Throttling time, in seconds, to wait between each
                              request.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the channel names / urls
                              you want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:
. Scraping a group's posts:
    $ minet telegram channel-messages nytimes > messages.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## Tiktok

```
usage: minet tiktok [-h] {search-videos} ...

Minet Tiktok Command
====================

Gather data from Tiktok.

optional arguments:
  -h, --help       show this help message and exit

subcommands:
  {search-videos}  Subcommand to use.
```

### search-videos

```
usage: minet tiktok search-videos [-h] [-c COOKIE] [--rcfile RCFILE] [-l LIMIT]
                                  [-i INPUT] [-s SELECT] [-o OUTPUT]
                                  value_or_column_name

Tiktok Search Videos Command
============================

Scrape Tiktok videos with given keyword(s).

This requires to be logged in to an Tiktok account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

Challenges are hashtags, that can be associated with a description.

The url have a limited life time (indicated by a timestamp in the
url). If you want to get the resources associated to it, you should
use the `minet fetch` command.

This command allows you to get about 450 results, ordered by user
relevance (a mix of most popular, and most relevant according to your
profile).

positional arguments:
  value_or_column_name        Single tiktok keyword to process or name of the
                              CSV column containing tiktok keywords when using
                              -i/--input.

optional arguments:
  -c COOKIE, --cookie COOKIE  Authenticated cookie to use or browser from which
                              to extract it (supports "firefox", "chrome",
                              "chromium", "opera" and "edge"). Defaults to
                              "firefox". Can also be configured in a .minetrc
                              file as "tiktok.cookie" or read from the
                              MINET_TIKTOK_COOKIE env variable.
  -l LIMIT, --limit LIMIT     Maximum number of videos to retrieve per query.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the tiktok keywords you
                              want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Searching videos with the keyword paris:
    $ minet tiktok search-videos paris > paris_videos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## Twitter

### attrition

```
usage: minet twitter attrition [-h] [--user USER] [--retweeted-id RETWEETED_ID]
                               [--ids] [--api-key API_KEY] [--rcfile RCFILE]
                               [--api-secret-key API_SECRET_KEY]
                               [--access-token ACCESS_TOKEN]
                               [--access-token-secret ACCESS_TOKEN_SECRET]
                               [-i INPUT] [-s SELECT] [--total TOTAL] [--resume]
                               [-o OUTPUT]
                               value_or_column_name

Minet Twitter Attrition Command
===============================

Using Twitter API to find whether batches of tweets are still
available today and if they aren't, attempt to find a reason why.

This command relies on tweet ids or tweet urls. We recommand to add `--user` and
the tweet's user id to the command if you can, as more information can
be obtained when the user id (or the full url) is known.

The same can be said about retweet information and the `--retweeted-id` flag.

The command will output a report similar to the input file and
containing an additional column named "current_tweet_status" that can take
the following values:

    - "available_tweet": tweet is still available.
    - "user_or_tweet_deleted": tweet was deleted or its author was deactivated. To know whether it is one or the other reason
                                for unavailability that is the right one, add --user to the command.
    - "suspended_user": tweet cannot be found because its user is suspended.
    - "deactivated_user": tweet cannot be found because its user is deactivated.
    - "deactivated_or_renamed_user": tweet cannot be found because its user is either deactivated or changed its screen name
                                        (only when using tweet urls or tweet ids and screen names instead of user ids).
    - "protected_user": tweet cannot be found because its user is protected.
    - "censored_tweet": tweet is unavailable because it was consored by Twitter.
    - "blocked_by_tweet_author": tweet cannot be found because you were blocked by its author.
    - "unavailable_tweet": tweet is not available, which means it was
                            deleted by its user.
    - "unavailable_retweet": retweet is not available, meaning that the user
                                cancelled their retweet.
    - "unavailable_retweeted_tweet": the retweeted tweet is unavailable,
                                        meaning it was either deleted by its original
                                        user or the original user was deactivated.
    - "censored_retweeted_tweet": the original tweet was censored by Twitter, making the retweet unavailable.
    - "protected_retweeted_user": tweet cannot be found because it is a retweet of a protected user.
    - "suspended_retweeted_user": tweet cannot be found because it is a retweet of a suspended user.
    - "blocked_by_original_tweet_author": tweet cannot be found because it is a retweet of a user who blocked you.

positional arguments:
  value_or_column_name          Single tweet url or id to process or name of the
                                CSV column containing tweet urls or ids when
                                using -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  --ids                         Whether your users are given as ids rather than
                                screen names.
  --retweeted-id RETWEETED_ID   Name of the column containing the ids of the
                                original tweets in case the tweets no longer
                                available were retweets.
  --user USER                   Name of the column containing the tweet's author
                                (given as ids or screen names). This is useful
                                to have more information on a tweet's
                                unavailability.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the tweet urls or ids
                                you want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Finding out if tweets in a CSV files are still available or not using tweet ids:
    $ minet tw attrition tweet_url deleted_tweets.csv > attrition-report.csv

. Finding out if tweets are still available or not using tweet & user ids:
    $ minet tw attrition tweet_id deleted_tweets.csv --user user_id --ids > attrition-report.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### followers

```
usage: minet twitter followers [-h] [--ids] [--v2] [--api-key API_KEY]
                               [--rcfile RCFILE]
                               [--api-secret-key API_SECRET_KEY]
                               [--access-token ACCESS_TOKEN]
                               [--access-token-secret ACCESS_TOKEN_SECRET]
                               [-i INPUT] [-s SELECT] [--total TOTAL] [--resume]
                               [-o OUTPUT]
                               value_or_column_name

Minet Twitter Followers Command
===============================

Retrieve followers, i.e. followed users, of given user.

positional arguments:
  value_or_column_name          Single Twitter account screen name or id to
                                process or name of the CSV column containing
                                Twitter account screen names or ids when using
                                -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  --ids                         Whether your users are given as ids rather than
                                screen names.
  --v2                          Whether to use latest Twitter API v2 rather than
                                v1.1.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the Twitter account
                                screen names or ids you want to process. Will
                                consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Getting followers of a list of user:
    $ minet tw followers screen_name users.csv > followers.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### friends

```
usage: minet twitter friends [-h] [--ids] [--v2] [--api-key API_KEY]
                             [--rcfile RCFILE] [--api-secret-key API_SECRET_KEY]
                             [--access-token ACCESS_TOKEN]
                             [--access-token-secret ACCESS_TOKEN_SECRET]
                             [-i INPUT] [-s SELECT] [--total TOTAL] [--resume]
                             [-o OUTPUT]
                             value_or_column_name

Minet Twitter Friends Command
=============================

Retrieve friends, i.e. followed users, of given user.

positional arguments:
  value_or_column_name          Single Twitter account screen name or id to
                                process or name of the CSV column containing
                                Twitter account screen names or ids when using
                                -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  --ids                         Whether your users are given as ids rather than
                                screen names.
  --v2                          Whether to use latest Twitter API v2 rather than
                                v1.1.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the Twitter account
                                screen names or ids you want to process. Will
                                consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Getting friends of a list of user:
    $ minet tw friends screen_name users.csv > friends.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### list-followers

```
usage: minet twitter list-followers [-h] [--api-key API_KEY] [--rcfile RCFILE]
                                    [--api-secret-key API_SECRET_KEY]
                                    [--access-token ACCESS_TOKEN]
                                    [--access-token-secret ACCESS_TOKEN_SECRET]
                                    [-i INPUT] [-s SELECT] [--total TOTAL]
                                    [-o OUTPUT]
                                    value_or_column_name

Minet Twitter List Followers Command
====================================

Retrieve followers of given list using Twitter API v2.

positional arguments:
  value_or_column_name          Single Twitter list id or url to process or name
                                of the CSV column containing Twitter list ids or
                                urls when using -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the Twitter list ids or
                                urls you want to process. Will consider `-` as
                                stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Getting followers of a list of lists:
    $ minet tw list-followers id lists.csv > followers.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### list-members

```
usage: minet twitter list-members [-h] [--api-key API_KEY] [--rcfile RCFILE]
                                  [--api-secret-key API_SECRET_KEY]
                                  [--access-token ACCESS_TOKEN]
                                  [--access-token-secret ACCESS_TOKEN_SECRET]
                                  [-i INPUT] [-s SELECT] [--total TOTAL]
                                  [-o OUTPUT]
                                  value_or_column_name

Minet Twitter List Members Command
==================================

Retrieve members of given list using Twitter API v2.

positional arguments:
  value_or_column_name          Single Twitter list id or url to process or name
                                of the CSV column containing Twitter list ids or
                                urls when using -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the Twitter list ids or
                                urls you want to process. Will consider `-` as
                                stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Getting members of a list of lists:
    $ minet tw list-members id lists.csv > members.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### retweeters

```
usage: minet twitter retweeters [-h] [--api-key API_KEY] [--rcfile RCFILE]
                                [--api-secret-key API_SECRET_KEY]
                                [--access-token ACCESS_TOKEN]
                                [--access-token-secret ACCESS_TOKEN_SECRET]
                                [-i INPUT] [-s SELECT] [--total TOTAL]
                                [-o OUTPUT]
                                value_or_column_name

Minet Twitter Retweeters Command
================================

Retrieve retweeters of given tweet using Twitter API v2.

positional arguments:
  value_or_column_name          Single tweet id to process or name of the CSV
                                column containing tweet ids when using
                                -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the tweet ids you want
                                to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Getting the users who retweeted a list of tweets:
    $ minet tw retweeters tweet_id tweets.csv > retweeters.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="twitter-scrape">scrape</h3>

```
usage: minet twitter scrape [-h] [--include-refs] [-l LIMIT]
                            [--query-template QUERY_TEMPLATE] [-i INPUT]
                            [-s SELECT] [-o OUTPUT]
                            {tweets,users} value_or_column_name

Minet Twitter Scrape Command
============================

Scrape Twitter's public facing search API to collect tweets or users.

Be sure to check Twitter's advanced search to check what kind of
operators you can use to tune your queries (time range, hashtags,
mentions, boolean etc.):
https://twitter.com/search-advanced?f=live

Useful operators include "since" and "until" to search specific
time ranges like so: "since:2014-01-01 until:2017-12-31".

BEWARE: the web search results seem to become inconsistent when
queries return vast amounts of tweets. In which case you are
strongly advised to segment your queries using temporal filters.

positional arguments:
  {tweets,users}                What to scrape. Currently only allows for
                                `tweets` or `users`.
  value_or_column_name          Single query to process or name of the CSV
                                column containing queries when using -i/--input.

optional arguments:
  --include-refs                Whether to emit referenced tweets (quoted,
                                retweeted & replied) in the CSV output. Note
                                that it consumes a memory proportional to the
                                total number of unique tweets retrieved.
  -l LIMIT, --limit LIMIT       Maximum number of tweets or users to collect per
                                query.
  --query-template QUERY_TEMPLATE
                                Query template. Can be useful for instance to
                                change a column of twitter user screen names
                                into from:@user queries.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  -i INPUT, --input INPUT       CSV file containing all the queries you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  -h, --help                    show this help message and exit

examples:

. Collecting the latest 500 tweets of a given Twitter user:
    $ minet tw scrape tweets "from:@jack" --limit 500 > tweets.csv

. Collecting the tweets from multiple Twitter queries listed in a CSV file:
    $ minet tw scrape tweets query queries.csv > tweets.csv

. Templating the given CSV column to query tweets by users:
    $ minet tw scrape tweets user users.csv --query-template 'from:@{value}' > tweets.csv

. Tip: You can add a "OR @aNotExistingHandle" to your query to avoid searching
  for your query terms in usernames or handles.
  Note that this is a temporary hack which might stop working at any time so be
  sure to double check before relying on this trick.
  For more information see the related discussion here:
  https://webapps.stackexchange.com/questions/127425/how-to-exclude-usernames-and-handles-while-searching-twitter

    $ minet tw scrape tweets "keyword OR @anObviouslyNotExistingHandle"

. Collecting users with "adam" in their user_name or user_description:
    $ minet tw scrape users adam > users.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### tweet-date

```
usage: minet twitter tweet-date [-h] [--timezone TIMEZONE] [-i INPUT]
                                [-s SELECT] [-o OUTPUT]
                                value_or_column_name

Minet Twitter Tweet Date Command
================================

Getting timestamp and date from tweet url or id.

positional arguments:
  value_or_column_name        Single tweet url or id to process or name of the
                              CSV column containing tweet urls or ids when using
                              -i/--input.

optional arguments:
  --timezone TIMEZONE         Timezone for the date, for example 'Europe/Paris'.
                              Default to UTC.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  -i INPUT, --input INPUT     CSV file containing all the tweet urls or ids you
                              want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:

    $ minet tw tweet-date url tweets.csv --timezone 'Europe/Paris'> tweets_timestamp_date.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### tweet-search

```
usage: minet twitter tweet-search [-h] [--since-id SINCE_ID]
                                  [--until-id UNTIL_ID]
                                  [--start-time START_TIME]
                                  [--end-time END_TIME] [--academic]
                                  [--sort-order {recency,relevancy}]
                                  [--api-key API_KEY] [--rcfile RCFILE]
                                  [--api-secret-key API_SECRET_KEY]
                                  [--access-token ACCESS_TOKEN]
                                  [--access-token-secret ACCESS_TOKEN_SECRET]
                                  [-i INPUT] [-s SELECT] [--total TOTAL]
                                  [-o OUTPUT]
                                  value_or_column_name

Minet Twitter Tweets Search Command
===================================

Search Twitter tweets using API v2.

This will only return the last 8 days of results maximum per query (unless you have Academic Research access).

To search the full archive of public tweets, use --academic if you have academic research access.

positional arguments:
  value_or_column_name          Single query to process or name of the CSV
                                column containing queries when using -i/--input.

optional arguments:
  --academic                    Flag to add if you want to use your academic
                                research access (in order to search the complete
                                history of public tweets).
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  --end-time END_TIME           The UTC stamp to which the tweets will be
                                provided. The date should have the format :
                                YYYY-MM-DDTHH:mm:ssZ
  --since-id SINCE_ID           Will return tweets with ids that are greater
                                than the specified id. Takes precedence over
                                --start-time.
  --sort-order {recency,relevancy}
                                How to sort retrieved tweets. Defaults to
                                "recency".
  --start-time START_TIME       The oldest UTC stamp from which the tweets will
                                be provided. The date should have the format :
                                YYYY-MM-DDTHH:mm:ssZ
  --until-id UNTIL_ID           Will return tweets that are older than the tweet
                                with the specified id.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the queries you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Searching tweets using "cancer" as a query:
    $ minet tw tweet-search cancer > tweets.csv

. Running multiple queries in series:
    $ minet tw tweet-search query queries.csv > tweets.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### tweet-count

```
usage: minet twitter tweet-count [-h] [--granularity {day,hour,minute}]
                                 [--since-id SINCE_ID] [--until-id UNTIL_ID]
                                 [--start-time START_TIME] [--end-time END_TIME]
                                 [--academic] [--api-key API_KEY]
                                 [--rcfile RCFILE]
                                 [--api-secret-key API_SECRET_KEY]
                                 [--access-token ACCESS_TOKEN]
                                 [--access-token-secret ACCESS_TOKEN_SECRET]
                                 [-i INPUT] [-s SELECT] [--total TOTAL]
                                 [-o OUTPUT]
                                 value_or_column_name

Minet Twitter Tweets Count Command
==================================

Count the number of tweets matching the given query using Twitter's
latest API v2. The count's granularity can be at the level of tweets
per day, per hour, or per minute.

This will only return result for the last 8 days only, unless
you have Academic Research access in which case you
can use the --academic flag to retrieve the full count.

Be advised that, for now, results are returned unordered
by Twitter's API if you choose a time granularity for the
results.

positional arguments:
  value_or_column_name          Single query to process or name of the CSV
                                column containing queries when using -i/--input.

optional arguments:
  --academic                    Flag to add if you want to use your academic
                                research access (in order to search the complete
                                history of public tweets).
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  --end-time END_TIME           The UTC stamp to which the tweets will be
                                provided. The date should have the format :
                                YYYY-MM-DDTHH:mm:ssZ
  --granularity {day,hour,minute}
                                Granularity used to group the data by. Defaults
                                to day.
  --since-id SINCE_ID           Will return tweets with ids that are greater
                                than the specified id. Takes precedence over
                                --start-time.
  --start-time START_TIME       The oldest UTC stamp from which the tweets will
                                be provided. The date should have the format :
                                YYYY-MM-DDTHH:mm:ssZ
  --until-id UNTIL_ID           Will return tweets that are older than the tweet
                                with the specified id.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the queries you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Counting tweets using "cancer" as a query:
    $ minet tw tweet-count cancer

. Running multiple queries in series:
    $ minet tw tweet-count query queries.csv > counts.csv

. Number of tweets matching the query per day:
    $ minet tw tweet-count "query" --granularity day > counts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### tweets

```
usage: minet twitter tweets [-h] [--v2] [--api-key API_KEY] [--rcfile RCFILE]
                            [--api-secret-key API_SECRET_KEY]
                            [--access-token ACCESS_TOKEN]
                            [--access-token-secret ACCESS_TOKEN_SECRET]
                            [-i INPUT] [-s SELECT] [--total TOTAL] [--resume]
                            [-o OUTPUT]
                            value_or_column_name

Minet Twitter Tweets Command
============================

Collecting tweet metadata from the given tweet ids, using the API.

positional arguments:
  value_or_column_name          Single tweet id to process or name of the CSV
                                column containing tweet ids when using
                                -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  --v2                          Whether to use latest Twitter API v2 rather than
                                v1.1.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the tweet ids you want
                                to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Getting metadata from tweets in a CSV file:
    $ minet tw tweets tweet_id tweets.csv > tweets_metadata.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### users

```
usage: minet twitter users [-h] [--ids] [--v2] [--api-key API_KEY]
                           [--rcfile RCFILE] [--api-secret-key API_SECRET_KEY]
                           [--access-token ACCESS_TOKEN]
                           [--access-token-secret ACCESS_TOKEN_SECRET]
                           [-i INPUT] [-s SELECT] [--total TOTAL] [--resume]
                           [-o OUTPUT]
                           value_or_column_name

Minet Twitter Users Command
===========================

Retrieve Twitter user metadata using the API.

positional arguments:
  value_or_column_name          Single Twitter user to process or name of the
                                CSV column containing Twitter users when using
                                -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  --ids                         Whether your users are given as ids rather than
                                screen names.
  --v2                          Whether to use latest Twitter API v2 rather than
                                v1.1.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the Twitter users you
                                want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Getting friends of a list of user:
    $ minet tw users screen_name users.csv > data_users.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### user-search

```
usage: minet twitter user-search [-h] [--api-key API_KEY] [--rcfile RCFILE]
                                 [--api-secret-key API_SECRET_KEY]
                                 [--access-token ACCESS_TOKEN]
                                 [--access-token-secret ACCESS_TOKEN_SECRET]
                                 [-i INPUT] [-s SELECT] [--total TOTAL]
                                 [-o OUTPUT]
                                 value_or_column_name

Minet Twitter Users Search Command
==================================

Search Twitter users using API v1.

This will only return ~1000 results maximum per query
so you might want to find a way to segment your inquiry
into smaller queries to find more users.

positional arguments:
  value_or_column_name          Single query to process or name of the CSV
                                column containing queries when using -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the queries you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Searching user using "cancer" as a query:
    $ minet tw user-search cancer > users.csv

. Running multiple queries in series:
    $ minet tw user-search query queries.csv > users.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### user-tweets

```
usage: minet twitter user-tweets [-h] [--ids] [--min-date MIN_DATE]
                                 [--exclude-retweets] [--v2] [--api-key API_KEY]
                                 [--rcfile RCFILE]
                                 [--api-secret-key API_SECRET_KEY]
                                 [--access-token ACCESS_TOKEN]
                                 [--access-token-secret ACCESS_TOKEN_SECRET]
                                 [-i INPUT] [-s SELECT] [--total TOTAL]
                                 [-o OUTPUT]
                                 value_or_column_name

Minet Twitter User Tweets Command
=================================

Retrieve the last ~3200 tweets, including retweets from
the given Twitter users, using the API.

positional arguments:
  value_or_column_name          Single Twitter account screen name or id to
                                process or name of the CSV column containing
                                Twitter account screen names or ids when using
                                -i/--input.

optional arguments:
  --access-token ACCESS_TOKEN   Twitter API access token. Can also be configured
                                in a .minetrc file as "twitter.access_token" or
                                read from the MINET_TWITTER_ACCESS_TOKEN env
                                variable.
  --access-token-secret ACCESS_TOKEN_SECRET
                                Twitter API access token secret. Can also be
                                configured in a .minetrc file as
                                "twitter.access_token_secret" or read from the
                                MINET_TWITTER_ACCESS_TOKEN_SECRET env variable.
  --api-key API_KEY             Twitter API key. Can also be configured in a
                                .minetrc file as "twitter.api_key" or read from
                                the MINET_TWITTER_API_KEY env variable.
  --api-secret-key API_SECRET_KEY
                                Twitter API secret key. Can also be configured
                                in a .minetrc file as "twitter.api_secret_key"
                                or read from the MINET_TWITTER_API_SECRET_KEY
                                env variable.
  --exclude-retweets            Whether to exclude retweets from the output.
  --ids                         Whether your users are given as ids rather than
                                screen names.
  --min-date MIN_DATE           Whether to add a date to stop at for user's
                                tweets retrieval. UTC date should have the
                                following format : YYYY-MM-DD
  --v2                          Whether to use latest Twitter API v2 rather than
                                v1.1.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the Twitter account
                                screen names or ids you want to process. Will
                                consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

examples:

. Getting tweets from users in a CSV file:
    $ minet tw user-tweets screen_name users.csv > tweets.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

## Youtube

### captions

```
usage: minet youtube captions [-h] [--lang LANG] [-i INPUT] [-s SELECT]
                              [--total TOTAL] [-o OUTPUT]
                              value_or_column_name

Youtube captions
================

Retrieve captions for the given YouTube videos.

positional arguments:
  value_or_column_name        Single video url or id to process or name of the
                              CSV column containing video urls or ids when using
                              -i/--input.

optional arguments:
  --lang LANG                 Language (ISO code like "en") of captions to
                              retrieve. You can specify several languages by
                              preferred order separated by commas. Defaults to
                              "en".
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the video urls or ids you
                              want to process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  -h, --help                  show this help message and exit

examples:

. Fetching captions for a list of videos:
    $ minet yt captions video_id videos.csv > captions.csv

. Fetching French captions with a fallback to English:
    $ minet yt captions video_id videos.csv --lang fr,en > captions.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### channel-videos

```
usage: minet youtube channel-videos [-h] [-k KEY] [--rcfile RCFILE] [-i INPUT]
                                    [-s SELECT] [--total TOTAL] [-o OUTPUT]
                                    value_or_column_name

Youtube channel videos
======================

Retrieve metadata about all Youtube videos from one or many channel(s) using the API.

Under the hood, this command extract the channel id from the given url or scrape the
website to find it if necessary. Then the command uses the API to retrieve
information about videos stored in the main playlist of the channel
supposed to contain all the channel's videos.

positional arguments:
  value_or_column_name        Single channel to process or name of the CSV
                              column containing channels when using -i/--input.

optional arguments:
  -k KEY, --key KEY           YouTube API Data dashboard API key. Can be used
                              more than once. Can also be configured in a
                              .minetrc file as "youtube.key" or read from the
                              MINET_YOUTUBE_KEY env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the channels you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Fetching all the videos from a channel based on the channel's id or url:
    $ minet youtube channel-videos https://www.youtube.com/c/LinksOff -k my-api-key > linksoff_videos.csv
    $ minet youtube channel-videos https://www.youtube.com/channel/UCqnbDFdCpuN8CMEg0VuEBqA -k my-api-key > thenewyorktimes_videos.csv
    $ minet youtube channel-videos UCprclkVrNPls7PR-nHhf1Ow -k my-api-key > tonyheller_videos.csv

. Fetching multiple channels' videos:
    $ minet youtube channel-videos channel_id channels_id.csv -k my-api-key > channels_videos.csv
    $ minet youtube channel-videos channel_url channels_url.csv -k my-api-key > channels_videos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="youtube-comments">comments</h3>

### channels

```
usage: minet youtube channels [-h] [-k KEY] [--rcfile RCFILE] [-i INPUT]
                              [-s SELECT] [--total TOTAL] [-o OUTPUT]
                              value_or_column_name

Youtube Channels Command
========================

Retrieve metadata about Youtube channel from one or many name(s) using the API.

Under the hood, this command extract the channel id from the given url or scrape the
website to find it if necessary. Then the command uses the API to retrieve
information about the channel.

positional arguments:
  value_or_column_name        Single channel to process or name of the CSV
                              column containing channels when using -i/--input.

optional arguments:
  -k KEY, --key KEY           YouTube API Data dashboard API key. Can be used
                              more than once. Can also be configured in a
                              .minetrc file as "youtube.key" or read from the
                              MINET_YOUTUBE_KEY env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the channels you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Fetching metadata from a channel based on the channel's id or url:
    $ minet youtube channels https://www.youtube.com/c/LinksOff -k my-api-key > linksoff_meta.csv
    $ minet youtube channels https://www.youtube.com/channel/UCqnbDFdCpuN8CMEg0VuEBqA -k my-api-key > thenewyorktimes_meta.csv
    $ minet youtube channels UCprclkVrNPls7PR-nHhf1Ow -k my-api-key > tonyheller_meta.csv

. Fetching multiple channels' metadata:
    $ minet youtube channels channel_id channels_id.csv -k my-api-key > channels.csv
    $ minet youtube channels channel_url channels_url.csv -k my-api-key > channels.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

```
usage: minet youtube comments [-h] [-k KEY] [--rcfile RCFILE] [-i INPUT]
                              [-s SELECT] [--total TOTAL] [-o OUTPUT]
                              value_or_column_name

Youtube comments
================

Retrieve metadata about Youtube comments using the API.

positional arguments:
  value_or_column_name        Single video to process or name of the CSV column
                              containing videos when using -i/--input.

optional arguments:
  -k KEY, --key KEY           YouTube API Data dashboard API key. Can be used
                              more than once. Can also be configured in a
                              .minetrc file as "youtube.key" or read from the
                              MINET_YOUTUBE_KEY env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the videos you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

example:

. Fetching a video's comments:
    $ minet yt comments https://www.youtube.com/watch?v=7JTb2vf1OQQ -k my-api-key > comments.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

<h3 id="youtube-search">search</h3>

```
usage: minet youtube search [-h] [-l LIMIT]
                            [--order {date,rating,relevance,title,videoCount,viewCount}]
                            [-k KEY] [--rcfile RCFILE] [-i INPUT] [-s SELECT]
                            [--total TOTAL] [-o OUTPUT]
                            value_or_column_name

Youtube search
==============

Search videos using the YouTube API.

Note that, even if undocumented, the API will never return
more than approx. 500 videos for a given query.

positional arguments:
  value_or_column_name          Single query to process or name of the CSV
                                column containing queries when using -i/--input.

optional arguments:
  -k KEY, --key KEY             YouTube API Data dashboard API key. Can be used
                                more than once. Can also be configured in a
                                .minetrc file as "youtube.key" or read from the
                                MINET_YOUTUBE_KEY env variable.
  -l LIMIT, --limit LIMIT       Maximum number of videos to retrieve per query.
  --order {date,rating,relevance,title,videoCount,viewCount}
                                Order in which videos are retrieved. The default
                                one is relevance.
  -s SELECT, --select SELECT    Columns of input CSV file to include in the
                                output (separated by `,`).
  --total TOTAL                 Total number of items to process. Necessary if
                                you want to display a finite progress indicator.
  -i INPUT, --input INPUT       CSV file containing all the queries you want to
                                process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT    Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here: https://github.com/mediala
                                b/minet/blob/master/docs/cli.md#minetrc
  -h, --help                    show this help message and exit

example:

. Searching videos about birds:
    $ minet youtube search bird -k my-api-key > bird_videos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

### videos

```
usage: minet youtube videos [-h] [-k KEY] [--rcfile RCFILE] [-i INPUT]
                            [-s SELECT] [--total TOTAL] [-o OUTPUT]
                            value_or_column_name

Youtube videos
==============

Retrieve metadata about Youtube videos using the API.

positional arguments:
  value_or_column_name        Single video to process or name of the CSV column
                              containing videos when using -i/--input.

optional arguments:
  -k KEY, --key KEY           YouTube API Data dashboard API key. Can be used
                              more than once. Can also be configured in a
                              .minetrc file as "youtube.key" or read from the
                              MINET_YOUTUBE_KEY env variable.
  -s SELECT, --select SELECT  Columns of input CSV file to include in the output
                              (separated by `,`).
  --total TOTAL               Total number of items to process. Necessary if you
                              want to display a finite progress indicator.
  -i INPUT, --input INPUT     CSV file containing all the videos you want to
                              process. Will consider `-` as stdin.
  -o OUTPUT, --output OUTPUT  Path to the output file. Will consider `-` as
                              stdout. If not given, results will also be printed
                              to stdout.
  --rcfile RCFILE             Custom path to a minet configuration file. More
                              info about this here: https://github.com/medialab/
                              minet/blob/master/docs/cli.md#minetrc
  -h, --help                  show this help message and exit

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

. Here is how to use a command with a single value:
    $ minet cmd "value"

. Here is how to use a command with a csv file:
    $ minet cmd column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet cmd column_name -i -
```

