# Minet Command Line Usage

## Summary

_Global utilities_

- [-h/--help/help](#h--help)
- [--version](#version)
- [minetrc config files](#minetrc-config-files)
- [minet environment variables](#minet-environment-variables)

_Generic commands_

- [cookies](#cookies)
- [crawl](#crawl)
- [focus-crawl](#focus-crawl)
- [fetch](#fetch)
- [extract](#extract)
- [resolve](#resolve)
- [scrape](#scrape)
- [screenshot](#screenshot)
- [url-extract](#url-extract)
- [url-join](#url-join)
- [url-parse](#url-parse)

_Platform-related commands_

- [bluesky (bsky)](#bluesky)
  - [firehose](#firehose)
  - [tap](#tap)
  - [posts](#posts)
  - [post-liked-by](#post-liked-by)
  - [post-quotes](#post-quotes)
  - [post-reposted-by](#post-reposted-by)
  - [resolve-handle](#resolve-handle)
  - [resolve-post-url](#resolve-post-url)
  - [search-posts](#search-posts)
  - [search-profiles](#search-profiles)
  - [profiles](#profiles)
  - [profile-follows](#profile-follows)
  - [profile-followers](#profile-followers)
  - [profile-posts](#profile-posts)

- [facebook (fb)](#facebook)
  - [url-likes](#url-likes)
- [google](#google)
  - [sheets](#sheets)
- [hyphe](#hyphe)
  - [crawl](#crawl)
  - [declare](#declare)
  - [destroy](#destroy)
  - [dump](#dump)
  - [reset](#reset)
  - [tag](#tag)
- [instagram (insta)](#instagram)
  - [comments](#comments)
  - [hashtag](#hashtag)
  - [location](#location)
  - [post-infos](#post-infos)
  - [user-followers](#user-followers)
  - [user-following](#user-following)
  - [user-infos](#user-infos-1)
  - [user-posts](#user-posts)
- [mediacloud (mc)](#mediacloud)
  - [medias](#medias)
  - [search](#search)
  - [topic](#topic)
    - [stories](#stories)
- [reddit (rd)](#reddit)
  - [comments](#comments-1)
  - [posts](#posts)
  - [user-comments](#user-comments)
  - [user-posrs](#user-posts-1)
- [telegram (tl)](#telegram)
  - [channel-infos](#channel-infos)
  - [channel-messages](#channel-messages)
- [tiktok (tk)](#tiktok)
  - [scrape-commercials](#scrape-commercials)
  - [search-commercials](#search-commercials)
  - [search-videos](#search-videos)
- [twitter](#twitter)
  - [attrition](#attrition)
  - [followers](#followers-1)
  - [followers-you-know](#followers-you-know)
  - [friends](#friends)
  - [list-followers](#list-followers)
  - [list-members](#list-members)
  - [retweeters](#retweeters)
  - [scrape](#scrape-1)
  - [tweet-date](#tweet-date)
  - [tweet-search](#tweet-search)
  - [tweet-count](#tweet-count)
  - [tweets](#tweets)
  - [users](#users)
  - [user-search](#user-search)
  - [user-tweets](#user-tweets)
- [wikipedia (wiki)](#wikipedia)
  - [pageviews](#pageviews)
- [youtube (yt)](#youtube)
  - [captions](#captions)
  - [channel-videos](#channel-videos)
  - [channels](#channels)
  - [comments](#comments-2)
  - [search](#search-1)
  - [videos](#videos)

## -h/--help

If you need help about a command, don't hesitate to use the `-h/--help` flag or the `help` command:

```
minet ct posts -h
# or:
minet ct posts --help
# or
minet help ct posts
```

## --version

To check the installed version of `minet`, you can use the `--version` flag:

```
minet --version
>>> minet x.x.x
```

## minetrc config files

Minet supports configuration files so you can skip some tedious command line arguments that you would need to provide each time you call `minet` otherwise (such as `--key` for `youtube` commands).

Those configuration files can be written in YAML or JSON and can either be passed to minet using the `--rcfile` argument or will be searched at the following paths (with this precedence):

- `./.minetrc{,.yml,.yaml,.json}`
- `~/.minetrc{,.yml,.yaml,.json}`

_Configuration file_

```yml
---
bluesky:
  identifier: "MY_BLUESKY_IDENTIFIER" # Used as --identifier for `minet bsky` commands
  password: "MY_BLUESKY_APP_PASSWORD" # Used as --password for `minet bsky` commands
instagram:
  cookie: "MY_INSTAGRAM_COOKIE" # Used as --cookie for `minet insta` commands
mediacloud:
  token: "MY_MC_TOKEN" # Used as --token for `minet mc` commands
tiktok:
  cookie: "MY_TIKTOK_COOKIE" # Used as --cookie for `minet tk` commands
  api_key: "MY_TIKTOK_API_KEY" # Used as --api-key for `minet tk` commands
  api_secret: "MY_TIKTOK_API_SECRET" # Used as --api-secret for `minet tk` commands
twitter:
  cookie: "MY_TWITTER_COOKIE" # Used as --cookie for `minet tw scrape` command
  api_key: "MY_API_KEY" # Used as --api-key for `minet tw` commands
  api_secret_key: "MY_API_SECRET_KEY" # Used as --api-secret-key for `minet tw` commands
  access_token: "MY_ACCESS_TOKEN" # Used as --access-token for `minet tw` commands
  access_token_secret: "MY_ACCESS_TOKEN_SECRET" # Used as --access-token-secret for `minet tw` commands
youtube:
  key: "MY_YT_API_KEY" # Used as --key for `minet yt` commands
```

## minet environment variables

Alternatively you can also set some arguments using environment variables whose name starts with `MINET_` and followed by the proper key.

To build the name of the variable, first check what can be configured in a minet [rcfile](#minetrc-config-files) and build your variable name by joining its path using an underscore:

For instance, to override `youtube.key`, the variable will be `MINET_YOUTUBE_KEY`.

If one of the path's key already contains underscore, it will work all the same. So to override `twitter.api_key`, the variable will be `MINET_TWITTER_API_KEY`.

Note that the given variable will be cast to the proper type as if it was passed as a command line argument.

Finally note that command line arguments and flags will take precedence over environment variables, and that environment variables will take precedence over any rcfile configuration, but you can of course mix and match.

## cookies

```
Usage: minet cookies [-h] [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                     [--simple-progress] [--csv] [--url URL] [-o OUTPUT]
                     {brave,chrome,chromium,edge,firefox,opera,opera_gx,safari,vivaldi}

# Minet Cookies Command

Grab cookies directly from your browsers to use them easily later
in python scripts, for instance.

Positional Arguments:
  {brave,chrome,chromium,edge,firefox,opera,opera_gx,safari,vivaldi}
                                Name of the browser from which to grab cookies.

Optional Arguments:
  --csv                         Whether to format the output as CSV. If --url is
                                set, will output the cookie's morsels as CSV.
  --url URL                     If given, only returns full cookie header value
                                for this url.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

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
Usage: minet crawl [-h] [-O OUTPUT_DIR] [--silent]
                   [--refresh-per-second REFRESH_PER_SECOND] [--simple-progress]
                   [--resume] [--max-depth MAX_DEPTH] [--throttle THROTTLE]
                   [--domain-parallelism DOMAIN_PARALLELISM] [-t THREADS] [-z]
                   [--compress-transfer] [-w] [-d]
                   [--folder-strategy FOLDER_STRATEGY] [-f {csv,jsonl,ndjson}]
                   [-v] [-u] [-n] [-k] [--spoof-user-agent] [-p PROCESSES]
                   [--connect-timeout CONNECT_TIMEOUT] [--timeout TIMEOUT]
                   [--retries RETRIES] [--stateful-redirects] [--pycurl]
                   [--sqlar] [-m MODULE] [--factory]
                   [--input-spider INPUT_SPIDER] [-i INPUT] [--explode EXPLODE]
                   [-s SELECT] [--total TOTAL]
                   [url_or_url_column]

# Minet Crawl Command

Run a crawl using a minet crawler or spiders defined
in a python module.

Positional Arguments:
  url_or_url_column             Single start url to process or name of the CSV
                                column containing start urls when using
                                -i/--input. Defaults to "url".

Optional Arguments:
  -z, --compress-on-disk        Whether to compress the downloaded files when
                                saving files on disk.
  --compress-transfer           Whether to send a "Accept-Encoding" header
                                asking for a compressed response. Usually better
                                for bandwidth but at the cost of more CPU work.
  --connect-timeout CONNECT_TIMEOUT
                                Maximum socket connection time to host. Defaults
                                to `5`.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to `1`.
  --factory                     Whether crawl target is a crawler factory
                                function.
  --folder-strategy FOLDER_STRATEGY
                                Name of the strategy to be used to dispatch the
                                retrieved files into folders to alleviate issues
                                on some filesystems when a folder contains too
                                much files. Note that this will be applied on
                                top of --filename-template. All of the
                                strategies are described at the end of this
                                help. Defaults to `flat`.
  -f, --format {csv,jsonl,ndjson}
                                Serialization format for scraped/extracted data.
                                Defaults to `csv`.
  --input-spider INPUT_SPIDER   Name of the spider that will process jobs given
                                using -i/--input.
  -k, --insecure                Whether to allow ssl errors when performing
                                requests or not.
  --max-depth MAX_DEPTH         Maximum depth for the crawl.
  -m, --module MODULE           Python module to import to use as spider,
                                spiders or crawler factory. Suffix it with `:`
                                to give actual target within module e.g.
                                `package.module:spider`.
  -n, --normalized-url-cache    Whether to normalize url cache used to assess if
                                some url was already visited.
  -O, --output-dir OUTPUT_DIR   Output directory. Defaults to `crawl`.
  -p, --processes PROCESSES     Number of processes for the crawler process
                                pool.
  --pycurl                      Whether to use the pycurl library to perform the
                                calls.
  --retries RETRIES             Number of times to retry on timeout & common
                                network-related issues. Defaults to `0`.
  --spoof-user-agent            Whether to use a plausible random "User-Agent"
                                header when making requests.
  --sqlar                       Whether to write files into a single-file sqlite
                                archive rather than as individual files on the
                                disk.
  --stateful-redirects          Whether to keep a cookie jar while redirecting
                                and allowing self redirections that track state.
  -t, --threads THREADS         Number of threads to use. Will default to a
                                conservative number, based on the number of
                                available cores. Feel free to increase.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to `0.2`.
  --timeout TIMEOUT             Maximum time - in seconds - to spend for each
                                request before triggering a timeout. Defaults to
                                `30`.
  -v, --verbose                 Whether to print information about crawl
                                results.
  -u, --visit-urls-only-once    Whether to ensure that any url will only be
                                visited once.
  -d, --write-data, -D, --dont-write-data
                                Whether to write scraped/extracted data on disk.
                                Defaults to `True`.
  -w, --write-files             Whether to write downloaded files on disk in
                                order to save them for later.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the start urls you want to process. Will
                                consider `-` as stdin.
  --resume                      Whether to resume an interrupted crawl.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

--folder-strategy options:

. "flat": default choice, all files will be written in the indicated
    content folder.

. "fullpath": all files will be written in a folder consisting of the
    url hostname and then its path.

. "prefix-x": e.g. "prefix-4", files will be written in folders
    having a name that is the first x characters of the file's name.
    This is an efficient way to partition content into folders containing
    roughly the same number of files if the file names are random (which
    is the case by default since md5 hashes will be used).

. "hostname": files will be written in folders based on their url's
    full host name.

. "normalized-hostname": files will be written in folders based on
    their url's hostname stripped of some undesirable parts (such as
    "www.", or "m.", for instance).

. "fingerprinted-hostname": files will be written in folders based on
    their url's hostname stripped of some more undesirable parts (such as
    "fr.", for instance) and their public suffix will be dropped.

Examples:

. Using the most basic crawler following HTML links:
    $ minet crawl url -i urls.csv --max-depth 1

. Crawling using the `process` function from the `crawl` module:
    $ minet crawl -m crawl:process -O crawl-data

Notes regarding sqlite storage temporary files:

If you spawn a persistent crawler, some of its state will be kept using
specialized sqlite databases on disk.

Be aware that sqlite sometimes need to perform cleanup operations that rely
on temporary files that will be written in a folder configured as the
`SQLITE_TMPDIR` env variable. Be sure to set this variable when running this
command, especially when the crawler files will be stored on a different disk
and if writing in the host's `/tmp` directory can be risky due to insufficient
storage available.

For more info, check out: https://www.sqlite.org/tempfiles.html
```

## focus-crawl

```
Usage: minet focus-crawl [-h] [-C CONTENT_FILTER] [--silent]
                         [--refresh-per-second REFRESH_PER_SECOND]
                         [--simple-progress] [-U URL_FILTER]
                         [--invert-content-match] [--invert-url-match]
                         [--extract] [--irrelevant-continue] [--only-html]
                         [--extraction-fields EXTRACTION_FIELDS] [-O OUTPUT_DIR]
                         [--resume] [--max-depth MAX_DEPTH]
                         [--throttle THROTTLE]
                         [--domain-parallelism DOMAIN_PARALLELISM] [-t THREADS]
                         [-z] [--compress-transfer] [-w] [-d]
                         [--folder-strategy FOLDER_STRATEGY]
                         [-f {csv,jsonl,ndjson}] [-v] [-n] [-k]
                         [--spoof-user-agent] [-p PROCESSES]
                         [--connect-timeout CONNECT_TIMEOUT] [--timeout TIMEOUT]
                         [--retries RETRIES] [--stateful-redirects] [--pycurl]
                         [--sqlar] [--input-spider INPUT_SPIDER] [-i INPUT]
                         [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                         [url_or_url_column]

# Minet Focus Crawl Command

Minet crawl feature with the possibility
to use regular expressions to filter content.

Regex are not case sensitive, but
accents sensitive.

Regex must be written between simple quotes.

Positional Arguments:
  url_or_url_column             Single start url to process or name of the CSV
                                column containing start urls when using
                                -i/--input. Defaults to "url".

Optional Arguments:
  -z, --compress-on-disk        Whether to compress the downloaded files when
                                saving files on disk.
  --compress-transfer           Whether to send a "Accept-Encoding" header
                                asking for a compressed response. Usually better
                                for bandwidth but at the cost of more CPU work.
  --connect-timeout CONNECT_TIMEOUT
                                Maximum socket connection time to host. Defaults
                                to `5`.
  -C, --content-filter CONTENT_FILTER
                                Regex used to filter fetched content.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to `1`.
  --extract                     Perform regex match on extracted text content
                                instead of html content using the Trafilatura
                                library.
  --extraction-fields EXTRACTION_FIELDS
                                Fields of the trafilatura extraction you want to
                                apply the content filter on, separated using
                                commas. It must be used with the flag
                                `--extract`. Available flags are:
                                `canonical_url`, `title`, `description`,
                                `content`, `comments`, `author`, `categories`,
                                `tags`, `date` and `sitename`.
  --folder-strategy FOLDER_STRATEGY
                                Name of the strategy to be used to dispatch the
                                retrieved files into folders to alleviate issues
                                on some filesystems when a folder contains too
                                much files. Note that this will be applied on
                                top of --filename-template. All of the
                                strategies are described at the end of this
                                help. Defaults to `flat`.
  -f, --format {csv,jsonl,ndjson}
                                Serialization format for scraped/extracted data.
                                Defaults to `csv`.
  --input-spider INPUT_SPIDER   Name of the spider that will process jobs given
                                using -i/--input.
  -k, --insecure                Whether to allow ssl errors when performing
                                requests or not.
  --invert-content-match        Flag to turn the content filter into an
                                exclusion rule.
  --invert-url-match            Flag to turn the url filter into an exclusion
                                rule.
  --irrelevant-continue         Continue exploration whether met content is
                                relevant or not.
  --max-depth MAX_DEPTH         Maximum depth for the crawl.
  -n, --normalized-url-cache    Whether to normalize url cache used to assess if
                                some url was already visited.
  --only-html                   Add URLs to the crawler queue only if they seem
                                to lead to a HTML content.
  -O, --output-dir OUTPUT_DIR   Output directory. Defaults to `crawl`.
  -p, --processes PROCESSES     Number of processes for the crawler process
                                pool.
  --pycurl                      Whether to use the pycurl library to perform the
                                calls.
  --retries RETRIES             Number of times to retry on timeout & common
                                network-related issues. Defaults to `0`.
  --spoof-user-agent            Whether to use a plausible random "User-Agent"
                                header when making requests.
  --sqlar                       Whether to write files into a single-file sqlite
                                archive rather than as individual files on the
                                disk.
  --stateful-redirects          Whether to keep a cookie jar while redirecting
                                and allowing self redirections that track state.
  -t, --threads THREADS         Number of threads to use. Will default to a
                                conservative number, based on the number of
                                available cores. Feel free to increase.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to `0.2`.
  --timeout TIMEOUT             Maximum time - in seconds - to spend for each
                                request before triggering a timeout. Defaults to
                                `30`.
  -U, --url-filter URL_FILTER   Regex used to filter URLs added to crawler's
                                queue.
  -v, --verbose                 Whether to print information about crawl
                                results.
  -d, --write-data, -D, --dont-write-data
                                Whether to write scraped/extracted data on disk.
                                Defaults to `True`.
  -w, --write-files             Whether to write downloaded files on disk in
                                order to save them for later.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the start urls you want to process. Will
                                consider `-` as stdin.
  --resume                      Whether to resume an interrupted crawl.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

--folder-strategy options:

. "flat": default choice, all files will be written in the indicated
    content folder.

. "fullpath": all files will be written in a folder consisting of the
    url hostname and then its path.

. "prefix-x": e.g. "prefix-4", files will be written in folders
    having a name that is the first x characters of the file's name.
    This is an efficient way to partition content into folders containing
    roughly the same number of files if the file names are random (which
    is the case by default since md5 hashes will be used).

. "hostname": files will be written in folders based on their url's
    full host name.

. "normalized-hostname": files will be written in folders based on
    their url's hostname stripped of some undesirable parts (such as
    "www.", or "m.", for instance).

. "fingerprinted-hostname": files will be written in folders based on
    their url's hostname stripped of some more undesirable parts (such as
    "fr.", for instance) and their public suffix will be dropped.

Examples:

. Running a simple crawler:
    $ minet focus-crawl url -i urls.csv --content-filter '(?:assembl[ée]e nationale|s[ée]nat)' -O ./result

Notes regarding sqlite storage temporary files:

If you spawn a persistent crawler, some of its state will be kept using
specialized sqlite databases on disk.

Be aware that sqlite sometimes need to perform cleanup operations that rely
on temporary files that will be written in a folder configured as the
`SQLITE_TMPDIR` env variable. Be sure to set this variable when running this
command, especially when the crawler files will be stored on a different disk
and if writing in the host's `/tmp` directory can be risky due to insufficient
storage available.

For more info, check out: https://www.sqlite.org/tempfiles.html
```

## fetch

```
Usage: minet fetch [-h] [--domain-parallelism DOMAIN_PARALLELISM] [--silent]
                   [--refresh-per-second REFRESH_PER_SECOND] [--simple-progress]
                   [-t THREADS] [--throttle THROTTLE]
                   [--url-template URL_TEMPLATE] [--timeout TIMEOUT]
                   [-g {brave,chrome,chromium,edge,firefox,opera,opera_gx,safari,vivaldi}]
                   [-H HEADERS] [-k] [-X METHOD] [-x PROXY] [--spoof-user-agent]
                   [--retries RETRIES] [-f FILENAME_COLUMN]
                   [--filename-template FILENAME_TEMPLATE]
                   [--folder-strategy FOLDER_STRATEGY] [-O OUTPUT_DIR]
                   [--max-redirects MAX_REDIRECTS] [-z] [--compress-transfer]
                   [-c] [-D] [--keep-failed-contents] [--standardize-encoding]
                   [--only-html] [--pycurl] [--sqlar] [-i INPUT]
                   [--explode EXPLODE] [-s SELECT] [--total TOTAL] [--resume]
                   [-o OUTPUT]
                   url_or_url_column

# Minet Fetch Command

Use multiple threads to fetch batches of urls from a CSV file. The
command outputs a CSV report with additional metadata about the
HTTP calls and will generally write the retrieved files in a folder
given by the user.

Positional Arguments:
  url_or_url_column             Single url to process or name of the CSV column
                                containing urls when using -i/--input.

Optional Arguments:
  -z, --compress-on-disk        Whether to compress the contents.
  --compress-transfer           Whether to send a "Accept-Encoding" header
                                asking for a compressed response. Usually better
                                for bandwidth but at the cost of more CPU work.
  -c, --contents-in-report      Whether to include retrieved contents, e.g.
                                html, directly in the report and avoid writing
                                them in a separate folder. This requires to
                                standardize encoding and won't work on binary
                                formats.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to `1`.
  -f, --filename-column FILENAME_COLUMN
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
                                top of --filename-template. All of the
                                strategies are described at the end of this
                                help. Defaults to `flat`.
  -g, --grab-cookies {brave,chrome,chromium,edge,firefox,opera,opera_gx,safari,vivaldi}
                                Whether to attempt to grab cookies from your
                                computer's browser (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
  -H, --header HEADERS          Custom headers used with every requests.
  -k, --insecure                Whether to allow ssl errors when performing
                                requests or not.
  --keep-failed-contents        Whether to keep & write contents for failed
                                (i.e. non-200) http requests.
  --max-redirects MAX_REDIRECTS
                                Maximum number of redirections to follow before
                                breaking. Defaults to `10`.
  --only-html                   Only download urls if they are not unambiguously
                                not html (e.g. if the url has the .pdf or .jpg
                                extension etc.). Then, if the url was
                                downloaded, it will only be written on disk if
                                the http body actually looks like html.
  -O, --output-dir OUTPUT_DIR   Directory where the fetched files will be
                                written. Defaults to `downloaded`.
  -x, --proxy PROXY             Proxy server to use.
  --pycurl                      Whether to use the pycurl library to perform the
                                calls.
  -X, --request METHOD          The http method to use. Will default to GET.
                                Defaults to `GET`.
  --retries RETRIES             Number of times to retry on timeout & common
                                network-related issues. Defaults to `0`.
  -D, --dont-save               Use not to write any downloaded file on disk.
  --spoof-user-agent            Whether to use a plausible random "User-Agent"
                                header when making requests.
  --sqlar                       Whether to write files into a single-file sqlite
                                archive rather than as individual files on the
                                disk.
  --standardize-encoding        Whether to systematically convert retrieved text
                                to UTF-8.
  -t, --threads THREADS         Number of threads to use. Will default to a
                                conservative number, based on the number of
                                available cores. Feel free to increase.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to `0.2`.
  --timeout TIMEOUT             Maximum time - in seconds - to spend for each
                                request before triggering a timeout. Defaults to
                                ~30s.
  --url-template URL_TEMPLATE   A template for the urls to fetch. Handy e.g. if
                                you need to build urls from ids etc.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the urls you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Columns being added to the output:

. "original_index": index of the line in the original file (the output will be
    arbitrarily ordered since multiple requests are performed concurrently).
. "resolved_url": final resolved url (after templating & solving redirects).
. "http_status": HTTP status code of the request, e.g. 200, 404, 503 etc.
. "datetime_utc": datetime when the response was finished.
. "fetch_error": an error code if anything went wrong when performing the request.
. "path": path to the downloaded file, relative to the folder given
    through -O/--output-dir.
. "mimetype": detected mimetype of the requested file.
. "encoding": detected encoding of the requested file if relevant.
. "body_size": size of the downloaded document in bytes.
. "body": if -c/--contents-in-report is set, will contain the
    downloaded text and the files won't be written to disk.

--folder-strategy options:

. "flat": default choice, all files will be written in the indicated
    content folder.

. "fullpath": all files will be written in a folder consisting of the
    url hostname and then its path.

. "prefix-x": e.g. "prefix-4", files will be written in folders
    having a name that is the first x characters of the file's name.
    This is an efficient way to partition content into folders containing
    roughly the same number of files if the file names are random (which
    is the case by default since md5 hashes will be used).

. "hostname": files will be written in folders based on their url's
    full host name.

. "normalized-hostname": files will be written in folders based on
    their url's hostname stripped of some undesirable parts (such as
    "www.", or "m.", for instance).

. "fingerprinted-hostname": files will be written in folders based on
    their url's hostname stripped of some more undesirable parts (such as
    "fr.", for instance) and their public suffix will be dropped.

Examples:

. Fetching a single url (can be useful when piping):
    $ minet fetch "https://www.lemonde.fr"

. Fetching a batch of url from existing CSV file:
    $ minet fetch url -i file.csv > report.csv

. Piping to minet extract:
    $ minet fetch url -i file.csv -c | minet extract -i -

. CSV input from stdin (mind the `-`):
    $ xan select url file.csv | minet fetch url -i - > report.csv

. Downloading files in specific output directory:
    $ minet fetch url -i file.csv -O html > report.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet fetch "value"

. Here is how to use a command with a CSV file:
    $ minet fetch column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet fetch column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet fetch column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet fetch "value1,value2" --explode ","
```

## extract

```
Usage: minet extract [-h] [-g] [--silent]
                     [--refresh-per-second REFRESH_PER_SECOND]
                     [--simple-progress] [-I INPUT_DIR] [-p PROCESSES]
                     [--chunk-size CHUNK_SIZE] [--body-column BODY_COLUMN]
                     [--error-column ERROR_COLUMN]
                     [--status-column STATUS_COLUMN]
                     [--encoding-column ENCODING_COLUMN]
                     [--mimetype-column MIMETYPE_COLUMN] [--encoding ENCODING]
                     [-u] [-i INPUT] [--explode EXPLODE] [-s SELECT]
                     [--total TOTAL] [--resume] [-o OUTPUT]
                     [path_or_path_column]

# Minet Extract Command

Use multiple processes to extract the main textual content and various
metadata item from large batches of HTML files easily and efficiently.

Extraction of main content is performed using the `trafilatura` library
by Adrien Barbaresi.

Please note that this kind of main content extraction is heavily geared
towards press articles and might not be suited to other kinds of web pages.

More information about the library can be found here:
https://github.com/adbar/trafilatura

Note that this command has been geared towards working in tandem with
the fetch command. This means the command expects, by default, CSV files
containing columns like "path", "http_status", "encoding" etc. that
you can find in a fetch command CSV report.

This said, you can of course feed this command any kind of CSV data,
and use dedicated flags such as --status-column, --body-column to
to inform the command about your specific table.

The command is also able to work on glob patterns, such as: "downloaded/**/*.html",
and can also be fed CSV columns containing HTML content directly if
required.

Positional Arguments:
  path_or_path_column           Single path to process or name of the CSV column
                                containing paths when using -i/--input. Defaults
                                to "path".

Optional Arguments:
  --body-column BODY_COLUMN     Name of the CSV column containing html bodies.
                                Defaults to `body`.
  --chunk-size CHUNK_SIZE       Chunk size for multiprocessing. Defaults to `1`.
  --encoding ENCODING           Name of the default encoding to use. If not
                                given the command will infer it for you.
  --encoding-column ENCODING_COLUMN
                                Name of the CSV column containing file encoding.
                                Defaults to `encoding`.
  --error-column ERROR_COLUMN   Name of the CSV column containing a fetch error.
                                Defaults to `fetch_error`.
  -g, --glob                    Will interpret given paths as glob patterns to
                                resolve if given.
  -I, --input-dir INPUT_DIR     Directory where the HTML files are stored. Will
                                default to fetch default output directory.
  --mimetype-column MIMETYPE_COLUMN
                                Name of the CSV column containing file mimetype.
                                Defaults to `mimetype`.
  -p, --processes PROCESSES     Number of processes to use. Defaults to roughly
                                half of the available CPUs.
  --status-column STATUS_COLUMN
                                Name of the CSV column containing HTTP status.
                                Defaults to `http_status`.
  -u, --unordered               Whether to allow the result to be written in an
                                arbitrary order dependent on the multiprocessing
                                scheduling. Can improve performance.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the paths you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Columns being added to the output:

. "extract_original_index": index of the line in the original file (the output will be
    arbitrarily ordered since multiple requests are performed concurrently).
. "extract_error": any error that happened when extracting content.
. "canonical_url": canonical url of target html, extracted from
    link.
. "title": title of the web page, from <title> usually.
. "description": description of the web page, as found in its
    metadata.
. "content": main content of the web page as extracted.
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
. "image": main image of the web page when found.
. "pagetype": some page type as part of trafilatura's heuristics.

Examples:

. Extracting content from a single file on disk:
    $ minet extract ./path/to/file.html

. Extracting content from a `minet fetch` report:
    $ minet extract -i report.csv -I downloaded > extracted.csv

. Extracting content from a single url:
    $ minet fetch "https://lemonde.fr" | minet extract -i -

. Indicating a custom path column (e.g. "file"):
    $ minet extract file -i report.csv -I downloaded > extracted.csv

. Extracting content from a CSV column containing HTML directly:
    $ minet extract -i report.csv --body-column html > extracted.csv

. Extracting content from a bunch of files using a glob pattern:
    $ minet extract "./content/**/*.html" --glob > extracted.csv

. Extracting content using a CSV file containing glob patterns:
    $ minet extract pattern -i patterns.csv --glob > extracted.csv

. Working on a fetch report from stdin (mind the `-`):
    $ minet fetch url file.csv | minet extract -i - -I downloaded > extracted.csv
```

## resolve

```
Usage: minet resolve [-h] [--domain-parallelism DOMAIN_PARALLELISM] [--silent]
                     [--refresh-per-second REFRESH_PER_SECOND]
                     [--simple-progress] [-t THREADS] [--throttle THROTTLE]
                     [--url-template URL_TEMPLATE] [--timeout TIMEOUT]
                     [-g {brave,chrome,chromium,edge,firefox,opera,opera_gx,safari,vivaldi}]
                     [-H HEADERS] [-k] [-X METHOD] [-x PROXY]
                     [--spoof-user-agent] [--retries RETRIES]
                     [--max-redirects MAX_REDIRECTS] [--follow-meta-refresh]
                     [--follow-js-relocation] [--infer-redirection]
                     [--canonicalize] [--only-shortened] [-i INPUT]
                     [--explode EXPLODE] [-s SELECT] [--total TOTAL] [--resume]
                     [-o OUTPUT]
                     url_or_url_column

# Minet Resolve Command

Use multiple threads to resolve batches of urls from a CSV file. The
command outputs a CSV report with additional metadata about the
HTTP calls and the followed redirections.

Positional Arguments:
  url_or_url_column             Single url to process or name of the CSV column
                                containing urls when using -i/--input.

Optional Arguments:
  --canonicalize                Whether to extract the canonical url from the
                                html source code of the web page if found.
                                Requires to buffer part of the response body, so
                                it will slow things down.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to `1`.
  --follow-js-relocation        Whether to follow typical JavaScript window
                                relocation. Requires to buffer part of the
                                response body, so it will slow things down.
  --follow-meta-refresh         Whether to follow meta refresh tags. Requires to
                                buffer part of the response body, so it will
                                slow things down.
  -g, --grab-cookies {brave,chrome,chromium,edge,firefox,opera,opera_gx,safari,vivaldi}
                                Whether to attempt to grab cookies from your
                                computer's browser (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
  -H, --header HEADERS          Custom headers used with every requests.
  --infer-redirection           Whether to try to heuristically infer
                                redirections from the urls themselves, without
                                requiring a HTTP call.
  -k, --insecure                Whether to allow ssl errors when performing
                                requests or not.
  --max-redirects MAX_REDIRECTS
                                Maximum number of redirections to follow before
                                breaking. Defaults to `20`.
  --only-shortened              Whether to only attempt to resolve urls that are
                                probably shortened.
  -x, --proxy PROXY             Proxy server to use.
  -X, --request METHOD          The http method to use. Will default to GET.
                                Defaults to `GET`.
  --retries RETRIES             Number of times to retry on timeout & common
                                network-related issues. Defaults to `0`.
  --spoof-user-agent            Whether to use a plausible random "User-Agent"
                                header when making requests.
  -t, --threads THREADS         Number of threads to use. Will default to a
                                conservative number, based on the number of
                                available cores. Feel free to increase.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to `0.2`.
  --timeout TIMEOUT             Maximum time - in seconds - to spend for each
                                request before triggering a timeout. Defaults to
                                ~30s.
  --url-template URL_TEMPLATE   A template for the urls to fetch. Handy e.g. if
                                you need to build urls from ids etc.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the urls you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Columns being added to the output:

. "original_index": index of the line in the original file (the output will be
    arbitrarily ordered since multiple requests are performed concurrently).
. "resolved_url": final resolved url (after solving redirects).
. "http_status": HTTP status code of the request, e.g. 200, 404, 503 etc.
. "resolution_error": an error code if anything went wrong when performing the request.
. "redirect_count": total number of redirections to reach the final url.
. "redirect_chain": list of redirection types separated by "|".

Examples:

. Resolving a batch of url from existing CSV file:
    $ minet resolve url_column -i file.csv > report.csv

. CSV input from stdin (mind the `-`):
    $ xan select url_column file.csv | minet resolve url_column - > report.csv

. Resolving a single url:
    $ minet resolve https://lemonde.fr

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet fetch "value"

. Here is how to use a command with a CSV file:
    $ minet fetch column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet fetch column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet fetch column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet fetch "value1,value2" --explode ","
```

## scrape

For more documentation about minet's scraping DSL check this [page](../cookbook/scraping_dsl.md) from the Cookbook.

```
Usage: minet scrape [-h] [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                    [--simple-progress] [-m] [-e] [-g] [-I INPUT_DIR]
                    [-p PROCESSES] [--chunk-size CHUNK_SIZE]
                    [--body-column BODY_COLUMN] [--url-column URL_COLUMN]
                    [--error-column ERROR_COLUMN]
                    [--status-column STATUS_COLUMN]
                    [--encoding-column ENCODING_COLUMN]
                    [--mimetype-column MIMETYPE_COLUMN] [--encoding ENCODING]
                    [--base-url BASE_URL] [-f {csv,jsonl,ndjson}]
                    [--plural-separator PLURAL_SEPARATOR] [--strain STRAIN] [-u]
                    [--scraped-column-prefix SCRAPED_COLUMN_PREFIX] [-i INPUT]
                    [--explode EXPLODE] [-s SELECT] [--total TOTAL] [-o OUTPUT]
                    scraper [path_or_path_column]

# Minet Scrape Command

Use multiple processes to scrape data from a batch of HTML files using
minet scraping DSL documented here:
https://github.com/medialab/minet/blob/master/docs/cookbook/scraping_dsl.md
or a python function given using the -m/--module flag, or a simple inline
python expression given using the -e/--eval flag, or an already implemented
typical scraping routine (listed below).

It will output the scraped items as a CSV or NDJSON file.

Note that this command has been geared towards working in tandem with
the fetch command. This means the command expects, by default, CSV files
containing columns like "path", "http_status", "encoding" etc. that
you can find in a fetch command CSV report.

This said, you can of course feed this command any kind of CSV data,
and use dedicated flags such as --status-column, --body-column to
to inform the command about your specific table.

The command is also able to work on glob patterns, such as: "downloaded/**/*.html",
and can also be fed CSV columns containing HTML content directly if
required.

Note that a scraper can be "singular", i.e. emitting a single item per scraped
HTML file, or "plural" if it can emit 0 or n items per file.

Know that, for convenience, "singular" scraper will always emit a line
per line in your input, contrary to "plural" ones. This means that sometimes
said lines will be empty because the scraper did not match anything or if
an error occurred.

Positional Arguments:
  scraper                       Path to a scraper definition file, or name of a
                                builtin scraper, e.g. "title" (see the complete
                                list below), or a path to a python module and
                                function (e.g. scraper.py,
                                scraper.py:scrape_title).
  path_or_path_column           Single path to process or name of the CSV column
                                containing paths when using -i/--input. Defaults
                                to "path".

Optional Arguments:
  --base-url BASE_URL           Base url to use if --url-column is not valid.
  --body-column BODY_COLUMN     Name of the CSV column containing html bodies.
                                Defaults to `body`.
  --chunk-size CHUNK_SIZE       Chunk size for multiprocessing. Defaults to `1`.
  --encoding ENCODING           Name of the default encoding to use. If not
                                given the command will infer it for you.
  --encoding-column ENCODING_COLUMN
                                Name of the CSV column containing file encoding.
                                Defaults to `encoding`.
  --error-column ERROR_COLUMN   Name of the CSV column containing a fetch error.
                                Defaults to `fetch_error`.
  -e, --eval                    Whether given scraper should be a simple
                                expression to evaluate.
  -f, --format {csv,jsonl,ndjson}
                                Output format. Defaults to `csv`.
  -g, --glob                    Will interpret given paths as glob patterns to
                                resolve if given.
  -I, --input-dir INPUT_DIR     Directory where the HTML files are stored. Will
                                default to fetch default output directory.
  --mimetype-column MIMETYPE_COLUMN
                                Name of the CSV column containing file mimetype.
                                Defaults to `mimetype`.
  -m, --module                  Whether given scraper is a python target to
                                import.
  --plural-separator PLURAL_SEPARATOR
                                Separator use to join lists of values when
                                serializing to CSV. Defaults to `|`.
  -p, --processes PROCESSES     Number of processes to use. Defaults to roughly
                                half of the available CPUs.
  --scraped-column-prefix SCRAPED_COLUMN_PREFIX
                                Prefix to prepend to the names of columns added
                                by the scraper so they can be easily
                                distinguished from columns of the input.
  --status-column STATUS_COLUMN
                                Name of the CSV column containing HTTP status.
                                Defaults to `http_status`.
  --strain STRAIN               Optional CSS selector used to strain, i.e. only
                                parse matched tags in the parsed html files in
                                order to optimize performance.
  -u, --unordered               Whether to allow the result to be written in an
                                arbitrary order dependent on the multiprocessing
                                scheduling. Can improve performance.
  --url-column URL_COLUMN       Name of the CSV column containing the url.
                                Defaults to `resolved_url`.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the paths you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Builtin scrapers:

. "canonical": scrape the <link rel="canonical"> tag href if any.
. "metas": scrape the <meta> tags if any.
. "rss": scrape the RSS feed urls if any.
. "title": scrape the <title> tag if any.
. "urls": scrape all the relevant <a> tag href urls. Will join them
    with the correct base url if --url-column is valid.
. "images": scrape all the relevant <img> tag src urls. Will join them
    with the correct base url if --url-column is valid.
. "europresse": scrape the articles from europresse HTML files.

Examples:

. Scraping a single file on disk:
    $ minet scrape scraper.yml ./path/to/file.html

. Scraping a `minet fetch` report:
    $ minet scrape scraper.yml -i report.csv -I downloaded > scraped.csv

. Scraping a single url:
    $ minet fetch "https://lemonde.fr" | minet scrape scraper.yml -i -

. Using a builtin scraper:
    $ minet scrape title -i report.csv > titles.csv

. Using the `scrape` (default) function of target python module:
    $ minet scrape -m scraper.py -i report.csv > titles.csv

. Using the `scrape_title` function of target python module:
    $ minet scrape -m scraper.py:scrape_title -i report.csv > titles.csv

. Using an inline python expression to evaluate:
    $ minet scrape -e 'soup.scrape_one("title")' -i report.csv > titles.csv

. Indicating a custom path column (e.g. "file"):
    $ minet scrape scraper.yml file -i report.csv -I downloaded > scraped.csv

. Scraping a CSV column containing HTML directly:
    $ minet scrape scraper.yml -i report.csv --body-column html > scraped.csv

. Scraping a bunch of files using a glob pattern:
    $ minet scrape scraper.yml "./content/**/*.html" --glob > scraped.csv

. Scraping using a CSV file containing glob patterns:
    $ minet scrape scraper.yml pattern -i patterns.csv --glob > scraped.csv

. Working on a fetch report from stdin (mind the `-`):
    $ minet fetch url file.csv | minet scrape scraper.yml -i - -I downloaded > scraped.csv

. Yielding items as newline-delimited JSON (jsonl):
    $ minet scrape scraper.yml -i report.csv --format jsonl > scraped.jsonl

. Using a strainer to optimize performance:
    $ minet scrape links-scraper.yml --strain "a" -i report.csv > links.csv

. Keeping only some columns from input CSV file:
    $ minet scrape scraper.yml -i report.csv -s name,url > scraped.csv
```

## screenshot

```
Usage: minet screenshot [-h] [--domain-parallelism DOMAIN_PARALLELISM]
                        [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                        [--simple-progress] [-t THREADS] [--throttle THROTTLE]
                        [--url-template URL_TEMPLATE] [--timeout TIMEOUT]
                        [-f FILENAME_COLUMN]
                        [--filename-template FILENAME_TEMPLATE]
                        [--folder-strategy FOLDER_STRATEGY] [-O OUTPUT_DIR]
                        [--full-page] [--width WIDTH] [--height HEIGHT]
                        [--wait-until {commit,domcontentloaded,load,networkidle}]
                        [--adblock] [--automatic-consent] [--wait WAIT]
                        [-i INPUT] [--explode EXPLODE] [-s SELECT]
                        [--total TOTAL] [--resume] [-o OUTPUT]
                        url_or_url_column

# Minet Screenshot Command

Use multithreaded browser emulation to screenshot batches of urls
from a CSV file. The command outputs a CSV report with additional
metadata about the HTTP calls and the produced screenshots on disk.

Positional Arguments:
  url_or_url_column             Single url to process or name of the CSV column
                                containing urls when using -i/--input.

Optional Arguments:
  --adblock                     Whether to use the ublock-origin browser
                                extension.
  --automatic-consent           Whether to use the "I still don't care about
                                cookies" browser extension to try and get rid of
                                GDPR/cookies consent forms when screenshotting.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to `1`.
  -f, --filename-column FILENAME_COLUMN
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
                                top of --filename-template. All of the
                                strategies are described at the end of this
                                help. Defaults to `flat`.
  --full-page                   Whether to create full page screenshots.
  --height HEIGHT               Page height in pixels. Defaults to `1080`.
  -O, --output-dir OUTPUT_DIR   Directory where the screenshots will be written.
                                Defaults to `screenshots`.
  -t, --threads THREADS         Number of threads to use. Will default to a
                                conservative number, based on the number of
                                available cores. Feel free to increase.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to `0.2`.
  --timeout TIMEOUT             Maximum time - in seconds - to spend for each
                                request before triggering a timeout. Defaults to
                                ~30s.
  --url-template URL_TEMPLATE   A template for the urls to fetch. Handy e.g. if
                                you need to build urls from ids etc.
  --wait WAIT                   Time to wait, in seconds, before taking the
                                screenshot. This might be a good idea if none of
                                the --wait-until strategies work for you and if
                                you need to give more time to the browser
                                extensions to kick in. This obviously makes the
                                whole process slower.
  --wait-until {commit,domcontentloaded,load,networkidle}
                                What to wait to consider the web page loaded.
                                Defaults to `load`.
  --width WIDTH                 Page width in pixels. Defaults to `1920`.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the urls you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Columns being added to the output:

. "original_index": index of the line in the original file (the output will be
    arbitrarily ordered since multiple requests are performed concurrently).
. "http_status": HTTP status code of the request, e.g. 200, 404, 503 etc.
. "screenshot_error": an error code if anything went wrong when performing the request.
. "path": path to the downloaded file, relative to the folder given
    through -O/--output-dir.

--folder-strategy options:

{FolderStrategy.DOCUMENTATION}

Examples:

. Screenshot a batch of url from existing CSV file:
    $ minet screenshot url_column -i file.csv > report.csv

. CSV input from stdin (mind the `-`):
    $ xan select url_column file.csv | minet screenshot url_column - > report.csv

. Screenshot a single url:
    $ minet screenshot https://lemonde.fr

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet fetch "value"

. Here is how to use a command with a CSV file:
    $ minet fetch column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet fetch column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet fetch column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet fetch "value1,value2" --explode ","
```

## url-extract

```
Usage: minet url-extract [-h] [--silent]
                         [--refresh-per-second REFRESH_PER_SECOND]
                         [--simple-progress] [--base-url BASE_URL]
                         [--from {html,text}] [-s SELECT] [--total TOTAL]
                         [-o OUTPUT]
                         column input

# Minet Url Extract Command

Extract urls from a CSV column containing either raw text or raw
HTML.

Positional Arguments:
  column                        Name of the column containing text or html.
  input                         Target CSV file.

Optional Arguments:
  --base-url BASE_URL           Base url used to resolve relative urls.
  --from {html,text}            Extract urls from which kind of source? Defaults
                                to `text`.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Extracting urls from a text column:
    $ minet url-extract text -i posts.csv > urls.csv

. Extracting urls from a html column:
    $ minet url-extract html --from html -i posts.csv > urls.csv
```

## url-join

```
Usage: minet url-join [-h] [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                      [--simple-progress] [-p MATCH_COLUMN_PREFIX]
                      [--separator SEPARATOR] [-s SELECT] [-o OUTPUT]
                      column1 input1 column2 input2

# Minet Url Join Command

Join two CSV files by matching them on columns containing urls. It
works by indexing the first file's urls in a specialized
URL trie to match them with the second file's urls.

Positional Arguments:
  column1                       Name of the column containing urls in the
                                indexed file.
  input1                        Path to the file to index. Will understand `-`
                                as stdin.
  column2                       Name of the column containing urls in the second
                                file.
  input2                        Path to the second file. Will understand `-` as
                                stdin.

Optional Arguments:
  -p, --match-column-prefix MATCH_COLUMN_PREFIX
                                Optional prefix to add to the first file's
                                column names to avoid conflicts. Defaults to ``.
  --separator SEPARATOR         Split indexed url column by a separator?
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Joining two files:
    $ minet url-join url webentities.csv post_url posts.csv > joined.csv

. Adding a prefix to first file's column names:
    $ minet url-join -p w_ url webentities.csv post_url posts.csv > joined.csv

. Keeping only some columns from first file:
    $ minet url-join url webentities.csv post_url posts.csv -s url,id > joined.csv

. Reading one of the files from stdin:
    $ xan select url webentities.csv | minet url-join url - post_url posts.csv > joined.csv
```

## url-parse

```
Usage: minet url-parse [-h] [--facebook] [--silent]
                       [--refresh-per-second REFRESH_PER_SECOND]
                       [--simple-progress] [--twitter] [--youtube]
                       [--infer-redirection] [--fix-common-mistakes]
                       [--normalize-amp] [--quoted] [--sort-query]
                       [--strip-authentication] [--strip-fragment]
                       [--strip-index] [--strip-irrelevant-subdomains]
                       [--strip-protocol] [--strip-trailing-slash]
                       [--strip-suffix] [--platform-aware] [-i INPUT]
                       [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                       [-o OUTPUT]
                       url_or_url_column

# Minet Url Parse Command

Parse the urls contained in a CSV file using the python `ural`
library to extract useful information about them such as their
normalized version, domain name, etc.

Positional Arguments:
  url_or_url_column             Single url to process or name of the CSV column
                                containing urls when using -i/--input.

Optional Arguments:
  --facebook                    Whether to consider and parse the given urls as
                                coming from Facebook.
  --fix-common-mistakes, --dont-fix-common-mistakes
                                Whether or not to attempt to fix common URL
                                mistakes when normalizing url. Defaults to
                                `True`.
  --infer-redirection, --dont-infer-redirection
                                Whether or not to attempt resolving common
                                redirects by leveraging well-known GET
                                parameters when normalizing url. Defaults to
                                `True`.
  --normalize-amp, --dont-normalize-amp
                                Whether or not to attempt to normalize Google
                                AMP urls when normalizing url. Defaults to
                                `True`.
  --platform-aware              Whether url parsing should know about some
                                specific platform such as Facebook, YouTube etc.
                                into account when normalizing urls. Note that
                                this is different than activating --facebook or
                                --youtube.
  --quoted                      Whether to produce quoted canonical and
                                normalized version.
  --sort-query, --dont-sort-query
                                Whether or not to sort query items when
                                normalizing url. Defaults to `True`.
  --strip-authentication, --dont-strip-authentication
                                Whether or not to strip authentication when
                                normalizing url. Defaults to `True`.
  --strip-fragment, --dont-strip-fragment, --strip-fragment-except-routing
                                Whether or not to strip the url's fragment when
                                normalizing url. If set to
                                `--strip-fragment-except-routing`, will only
                                strip the fragment if the fragment is not deemed
                                to be js routing (i.e. if it contains a `/`).
                                Defaults to `except-routing`.
  --strip-index, --dont-strip-index
                                Whether or not to strip trailing index when
                                normalizing url. Defaults to `True`.
  --strip-irrelevant-subdomains, --dont-strip-irrelevant-subdomains
                                Whether or not to strip trailing
                                irrelevant-subdomains such as `www` etc. when
                                normalizing url. Defaults to `True`.
  --strip-protocol, --dont-strip-protocol
                                Whether or not to strip the protocol when
                                normalizing the url. Defaults to `True`.
  --strip-suffix                Whether to strip the hostname suffix when
                                fingerprinting the url.
  --strip-trailing-slash, --dont-strip-trailing-slash
                                Whether or not to trailing slash when
                                normalizing url. Defaults to `True`.
  --twitter                     Whether to consider and parse the given urls as
                                coming from Twitter.
  --youtube                     Whether to consider and parse the given urls as
                                coming from YouTube.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the urls you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Columns being added to the output:

. "canonicalized_url": url cleaned up but technically the same.
. "normalized_url": url aggressively normalized by removing any part
  that is not useful to determine which resource it is actually
  pointing at.
. "fingerprinted_url": url even more aggressively normalized. Might
  not be valid anymore, but useful for statistical aggregation.
. "inferred_redirection": redirection directly inferred from the
  url without needing to make any HTTP request.
. "domain_name": public suffix-aware domain name of the url.
. "hostname": full hostname of the url.
. "normalized_hostname": normalized hostname, i.e. stripped of "www",
  "m" or some language subdomains etc., of the url.
. "fingerprinted_hostname": hostname even more aggressively normalized.
  Might not be valid anymore.
. "probably_shortened": whether the url is probably shortened or
  not (bit.ly, t.co etc.).
. "probably_typo": whether the url probably contains typo or not
  (such as inclusive language in french : curieux.se etc.).
. "probably_homepage": whether the given url looks like a website's
  homepage.
. "should_resolve": whether the given url looks like something
  we should resolve, i.e. shortened url or DOI etc.
. "could_be_html": whether the given url could lead to a HTML file.
. "could_be_rss": whether the given url could lead to a RSS file.

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

Examples:

. Creating a report about a file's urls:
    $ minet url-parse url -i posts.csv > report.csv

. Keeping only selected columns from the input file:
    $ minet url-parse url -i posts.csv -s id,url,title > report.csv

. Parsing Facebook urls:
    $ minet url-parse url -i fbposts.csv --facebook > report.csv

. Parsing YouTube urls:
    $ minet url-parse url -i ytvideos.csv --youtube > report.csv

. Parsing Twitter urls:
    $ minet url-parse url -i tweets.csv --twitter > report.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet url-parse "value"

. Here is how to use a command with a CSV file:
    $ minet url-parse column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet url-parse column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet url-parse column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet url-parse "value1,value2" --explode ","
```

## Bluesky

```
Usage: minet bluesky [-h]
                     {firehose,tap,posts,post-liked-by,post-quotes,post-reposted-by,resolve-handle,resolve-post-url,search-posts,search-profiles,profiles,profile-followers,profile-follows,profile-posts}
                     ...

# Minet Bluesky command

Collect data from Bluesky.

Optional Arguments:
  -h, --help                    show this help message and exit

Subcommands:
  {firehose,tap,posts,post-liked-by,post-quotes,post-reposted-by,resolve-handle,resolve-post-url,search-posts,search-profiles,profiles,profile-followers,profile-follows,profile-posts}
                                Subcommand to use.
    firehose                    Minet Bluesky Firehose command
    tap                         Minet Bluesky Tap command (experimental)
    posts                       Minet Bluesky Get Post from URI or URL command
    post-liked-by               Minet Bluesky Get Liked By from URL or URI
                                command
    post-quotes                 Minet Bluesky Get Quotes from URL or URI command
    post-reposted-by            Minet Bluesky Get Reposted By from URL or URI
                                command
    resolve-handle              Minet Bluesky Resolve Handle command
    resolve-post-url            Minet Bluesky resolve URL to URI command
    search-posts                Minet Bluesky Search Post command
    search-profiles             Minet Bluesky Search Profiles command
    profiles                    Minet Bluesky Get Profile from Handle or DID
                                command
    profile-followers           Minet Bluesky Get Followers from Handle or DID
                                command
    profile-follows             Minet Bluesky Get Follows from Handle or DID
                                command
    profile-posts               Minet Bluesky Get Profile Posts command
```

### firehose

```
Usage: minet bluesky firehose [-h] [--since SINCE] [--silent]
                              [--refresh-per-second REFRESH_PER_SECOND]
                              [--simple-progress] [-o OUTPUT]

# Minet Bluesky Firehose command

Plug into the Bluesky Firehose.

Optional Arguments:
  --since SINCE                 Start collecting posts from the given datetime
                                (inclusive, timezone UTC). Note that the Bluesky
                                Jetstream firehose only allows to start from up
                                to one day in the past. Moreover, note that the
                                date used correspons to the firehose event
                                timestamp, only used for configuring or
                                debugging the firehose itself, so it might not
                                corresponds exactly to the first collected post
                                dates.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit
```

### tap

```
Usage: minet bluesky tap [-h] [-o OUTPUT] [--silent]
                         [--refresh-per-second REFRESH_PER_SECOND]
                         [--simple-progress]

# Minet Bluesky Tap command (experimental)

Plug into the Bluesky Tap socket. (experimental) Doc of Tap: https://docs.bsky.app/blog/introducing-tap

Optional Arguments:
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit
```

### posts

```
Usage: minet bluesky posts [-h] [--raw] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [--simple-progress] [--identifier IDENTIFIER]
                           [--rcfile RCFILE] [--password PASSWORD] [-i INPUT]
                           [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                           [-o OUTPUT]
                           post_or_post_column

# Minet Bluesky Get Post from URI or URL command

Get whether a Bluesky post given its URI or URL or multiple Bluesky posts given their URIs or URLs from the column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  post_or_post_column           Single post to process or name of the CSV column
                                containing posts when using -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  --raw                         Return the raw post data in JSON as received
                                from the Bluesky API instead of a normalized
                                version.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the posts you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get a post from its URI:
    $ minet bluesky posts <uri>

. Get a post from its URL:
    $ minet bluesky posts <url>

. Get multiple posts from their URIs from a CSV file:
    $ minet bluesky posts <uri-column> -i posts.csv

Tips:

- You can pass either Bluesky post URIs (at://did:...) or full URLs (https://bsky.app/profile/...) and Minet will handle the conversion for you.

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky posts "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky posts column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky posts column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky posts column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky posts "value1,value2" --explode ","
```

### post-liked-by

```
Usage: minet bluesky post-liked-by [-h] [-l LIMIT] [--silent]
                                   [--refresh-per-second REFRESH_PER_SECOND]
                                   [--simple-progress] [--identifier IDENTIFIER]
                                   [--rcfile RCFILE] [--password PASSWORD]
                                   [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                   [--total TOTAL] [-o OUTPUT]
                                   post_or_post_column

# Minet Bluesky Get Liked By from URL or URI command

Get profile who liked whether a post giving its URL or URI or several posts giving their URL or URI from the column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  post_or_post_column           Single post to process or name of the CSV column
                                containing posts when using -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  -l, --limit LIMIT             Limit the number of profiles to retrieve for
                                each post. Will collect all profiles by default.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the posts you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get profiles who liked a post from the post's URL:
    $ minet bluesky post-liked-by <post-url>

. Get 100 profiles who liked a post from the post's URI:
    $ minet bluesky post-liked-by <post-uri> --limit 100

. Get profiles who liked a post from post URLs from a CSV file:
    $ minet bluesky post-liked-by <url-column> -i posts.csv

Note:

- This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky post-liked-by "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky post-liked-by column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky post-liked-by column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky post-liked-by column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky post-liked-by "value1,value2" --explode ","
```

### post-quotes

```
Usage: minet bluesky post-quotes [-h] [-l LIMIT] [--silent]
                                 [--refresh-per-second REFRESH_PER_SECOND]
                                 [--simple-progress] [--identifier IDENTIFIER]
                                 [--rcfile RCFILE] [--password PASSWORD]
                                 [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                 [--total TOTAL] [-o OUTPUT]
                                 post_or_post_column

# Minet Bluesky Get Quotes from URL or URI command

Get whether posts quoting a post giving its URL or URI or several posts quoting several posts giving their URL or URI from the column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  post_or_post_column           Single post to process or name of the CSV column
                                containing posts when using -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  -l, --limit LIMIT             Limit the number of quotes to retrieve for each
                                post. Will collect all quotes by default.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the posts you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get quotes for a post's URL:
    $ minet bluesky post-quotes <post-url>

. Get 100 quotes for a post's URI:
    $ minet bluesky post-quotes <post-uri> --limit 100

. Get quotes for posts by URLs from a CSV file:
    $ minet bluesky post-quotes <url-column> -i posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky post-quotes "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky post-quotes column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky post-quotes column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky post-quotes column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky post-quotes "value1,value2" --explode ","
```

### post-reposted-by

```
Usage: minet bluesky post-reposted-by [-h] [-l LIMIT] [--silent]
                                      [--refresh-per-second REFRESH_PER_SECOND]
                                      [--simple-progress]
                                      [--identifier IDENTIFIER]
                                      [--rcfile RCFILE] [--password PASSWORD]
                                      [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                      [--total TOTAL] [-o OUTPUT]
                                      post_or_post_column

# Minet Bluesky Get Reposted By from URL or URI command

Get profile who reposted whether a post giving its URL or URI or several posts giving their URL or URI from the column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  post_or_post_column           Single post to process or name of the CSV column
                                containing posts when using -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  -l, --limit LIMIT             Limit the number of profiles to retrieve for
                                each post. Will collect all profiles by default.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the posts you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get profiles who reposted a post from the post's URL:
    $ minet bluesky post-reposted-by <post-url>

. Get 100 profiles who reposted a post from the post's URI:
    $ minet bluesky post-reposted-by <post-uri> --limit 100

. Get profiles who reposted a post from post URLs from a CSV file:
    $ minet bluesky post-reposted-by <url-column> -i posts.csv

Note:

- This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky post-reposted-by "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky post-reposted-by column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky post-reposted-by column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky post-reposted-by column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky post-reposted-by "value1,value2" --explode ","
```

### resolve-handle

```
Usage: minet bluesky resolve-handle [-h] [--identifier IDENTIFIER]
                                    [--rcfile RCFILE] [--silent]
                                    [--refresh-per-second REFRESH_PER_SECOND]
                                    [--simple-progress] [--password PASSWORD]
                                    [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                    [--total TOTAL] [-o OUTPUT]
                                    handle_or_handle_column

# Minet Bluesky Resolve Handle command

Resolve whether a Bluesky handle to its DID or multiple Bluesky handles to their DIDs from column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  handle_or_handle_column       Single handle to process or name of the CSV
                                column containing handles when using -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the handles you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get a profile DID from their handle:
    $ minet bluesky resolve-handle @bsky.app

. Get multiple profile DIDs from their handles from a CSV file:
    $ minet bluesky resolve-handle <handle-column> -i profiles.csv

Tips:

- You can pass the handle with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky resolve-handle "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky resolve-handle column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky resolve-handle column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky resolve-handle column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky resolve-handle "value1,value2" --explode ","
```

### resolve-post-url

```
Usage: minet bluesky resolve-post-url [-h] [--identifier IDENTIFIER]
                                      [--rcfile RCFILE] [--silent]
                                      [--refresh-per-second REFRESH_PER_SECOND]
                                      [--simple-progress] [--password PASSWORD]
                                      [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                      [--total TOTAL] [-o OUTPUT]
                                      url_or_url_column

# Minet Bluesky resolve URL to URI command

Resolve whether a Bluesky post URL to its URI or multiple Bluesky post URLs to their URIs from column of a CSV file. This command does not use the Bluesky HTTP API.

Positional Arguments:
  url_or_url_column             Single url to process or name of the CSV column
                                containing urls when using -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the urls you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get a post URI from its URL:
    $ minet bluesky resolve-post-url <url>

. Get multiple post URIs from their URLs from a CSV file:
    $ minet bluesky resolve-post-url <url-column> -i posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky resolve-post-url "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky resolve-post-url column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky resolve-post-url column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky resolve-post-url column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky resolve-post-url "value1,value2" --explode ","
```

### search-posts

```
Usage: minet bluesky search-posts [-h] [--lang LANG] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [--simple-progress] [--since SINCE]
                                  [--until UNTIL] [--mentions MENTIONS]
                                  [--author AUTHOR] [--domain DOMAIN]
                                  [--url URL] [-l LIMIT]
                                  [--identifier IDENTIFIER] [--rcfile RCFILE]
                                  [--password PASSWORD] [-i INPUT]
                                  [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [-o OUTPUT]
                                  query_or_query_column

# Minet Bluesky Search Post command

Search for whether Bluesky posts matching a query or multiple Bluesky posts matching respectively successives queries from column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  query_or_query_column         Single query to process or name of the CSV
                                column containing querys when using -i/--input.

Optional Arguments:
  --author AUTHOR               Filter posts by the given account (with or
                                without the @). Handles are resolved to DID
                                before query-time. Equivalent to
                                "from:<account>" in classic search syntax.
  --domain DOMAIN               Filter posts with URLs (facet links or embeds)
                                linking to the given domain (hostname). Server
                                may apply hostname normalization. Equivalent to
                                "domain:<domain>" in classic search syntax.
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  --lang LANG                   Filter posts in the given language. Expected to
                                be based on post language field, though server
                                may override language detection. Equivalent to
                                "lang:<lang>" in classic search syntax.
  -l, --limit LIMIT             Limit the number of posts to retrieve for each
                                query.
  --mentions MENTIONS           Filter posts which mention the given account
                                (with or without the @). Handles are resolved to
                                DID before query-time. Only matches rich-text
                                facet mentions. Equivalent to
                                "mentions:<account>" in classic search syntax.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  --since SINCE                 Filter results for posts after the indicated
                                datetime (inclusive). Expected to use
                                'createdAt' timestamp, with a millisecond
                                precision. Can be a datetime, or just an ISO
                                date (YYYY-MM-DD, YYYY-MM-DDTHH, ...,
                                YYYY-MM-DDTHH:mm:SSZ or
                                YYYY-MM-DDTHH:mm:SS.µSµSµSZ). Equivalent to
                                "since:<date>" in classic search syntax.
  --until UNTIL                 Filter results for posts before the indicated
                                datetime (NOT inclusive). Expected to use
                                'createdAt' timestamp, with a millisecond
                                precision. Can be a datetime, or just an ISO
                                date (YYYY-MM-DDTHH:mm:SSZ or
                                YYYY-MM-DDTHH:mm:SS.µSµSµSZ). Equivalent to
                                "until:<date>" in classic search syntax.
  --url URL                     Filter posts with links (facet links or embeds)
                                pointing to this URL. Server may apply URL
                                normalization or fuzzy matching. The only
                                equivalent in classic search syntax could be
                                typing the URL as a keyword.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the querys you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Collect last 500 posts containing the word "new" until 2024-01-01 at 16:15 UTC:
    $ minet bsky search-posts "new" --until 2024-01-01T16:15 --limit 500 > posts.csv

. Collect the posts containing the word "new" mentionning profile "alice.bsky.social" since 2025-01-01:
    $ minet bsky search-posts "new" --mentions alice.bsky.social --since 2025-01-01 > posts.csv

. Collect the posts containing the tag '#bluesky' in Spanish:
    $ minet bsky search-posts "#bluesky" -l es > posts.csv

. Collect the posts containing the word "bluesky" but not the word "twitter":
    $ minet bsky search-posts "bluesky -twitter" > posts.csv

. Collect the posts containing the word "bluesky" and a link to "youtube.com":
    $ minet bsky search-posts "bluesky" --domain youtube.com > posts.csv

Tips:

- You can use partial ISO dates (YYYY or YYYY-MM or YYYY-MM-DD or YYYY-MM-DDTHH or YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SS.ssssss) for the --since and --until arguments.

- To filter posts by given tags, use the hashtag syntax, e.g. "#bluesky" in the query. Multiple tags can be specified, with 'AND' matching.

- To filter posts without given keywords, use the minus syntax, e.g. "-twitter" in the query. Multiple keywords can be specified, with 'AND' matching.

Warning:

- After some tests, it seems that the posts returned by the Bluesky API are not always perfectly sorted by the local time we give (with millisecond precision). Indeed, this local time depends on the 'createdAt' field of the post, and we observed that in some cases, this value is artificial (cf their indexation code : https://github.com/bluesky-social/indigo/blob/c5eaa30f683f959af20ea17fdf390d8a22d471cd/search/transform.go#L225).

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky search-posts "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky search-posts column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky search-posts column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky search-posts column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky search-posts "value1,value2" --explode ","
```

### search-profiles

```
Usage: minet bluesky search-profiles [-h] [-l LIMIT] [--silent]
                                     [--refresh-per-second REFRESH_PER_SECOND]
                                     [--simple-progress]
                                     [--identifier IDENTIFIER] [--rcfile RCFILE]
                                     [--password PASSWORD] [-i INPUT]
                                     [--explode EXPLODE] [-s SELECT]
                                     [--total TOTAL] [-o OUTPUT]
                                     query_or_query_column

# Minet Bluesky Search Profiles command

Search for whether Bluesky profiles matching a query or multiple Bluesky profiles matching respectively successives queries from column of a CSV file. This command uses the Bluesky HTTP API. A profile matches a query if the profile's name, handle or bio matches the query. This command is equivalent to the classic search on Bluesky when filtering by 'People'.

Positional Arguments:
  query_or_query_column         Single query to process or name of the CSV
                                column containing querys when using -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  -l, --limit LIMIT             Limit the number of profiles to retrieve for
                                each query. Will collect all profiles by
                                default.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the querys you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Search profile by its handle:
    $ minet bluesky search-profiles @bsky.app

. Get 150 profiles from matching a query:
    $ minet bluesky search-profiles <query> --limit 150

. Get profiles from a CSV file:
    $ minet bluesky search-profiles <query-column> -i queries.csv

Note:

- This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky search-profiles "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky search-profiles column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky search-profiles column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky search-profiles column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky search-profiles "value1,value2" --explode ","
```

### profiles

```
Usage: minet bluesky profiles [-h] [--raw] [--silent]
                              [--refresh-per-second REFRESH_PER_SECOND]
                              [--simple-progress] [--identifier IDENTIFIER]
                              [--rcfile RCFILE] [--password PASSWORD] [-i INPUT]
                              [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                              [-o OUTPUT]
                              profile_or_profile_column

# Minet Bluesky Get Profile from Handle or DID command

Get whether a Bluesky profile given the profile handle or DID or multiple Bluesky profiles given their handles or DIDs from column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  profile_or_profile_column     Single profile to process or name of the CSV
                                column containing profiles when using
                                -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  --raw                         Return the raw profile data in JSON as received
                                from the Bluesky API instead of a normalized
                                version.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the profiles you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get profile by their handle:
    $ minet bluesky profiles @bsky.app

. Get profile by their DID:
    $ minet bluesky profiles did:plc:z72i7hdynmk6r22z27h6tvur

. Get profiles by their handles from a CSV file:
    $ minet bluesky profiles <handle-column> -i profiles.csv

Tips:

- If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky profiles "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky profiles column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky profiles column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky profiles column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky profiles "value1,value2" --explode ","
```

### profile-follows

```
Usage: minet bluesky profile-follows [-h] [-l LIMIT] [--silent]
                                     [--refresh-per-second REFRESH_PER_SECOND]
                                     [--simple-progress]
                                     [--identifier IDENTIFIER] [--rcfile RCFILE]
                                     [--password PASSWORD] [-i INPUT]
                                     [--explode EXPLODE] [-s SELECT]
                                     [--total TOTAL] [-o OUTPUT]
                                     profile_or_profile_column

# Minet Bluesky Get Follows from Handle or DID command

Get whether follows of a profile giving its handle or DID or respective follows of several profiles given their handle or did from the column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  profile_or_profile_column     Single profile to process or name of the CSV
                                column containing profiles when using
                                -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  -l, --limit LIMIT             Limit the number of follows to retrieve for each
                                profile. Will collect all follows by default.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the profiles you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get follows of a profile by their handle:
    $ minet bluesky profile-follows @bsky.app

. Get 100 follows of a profile by their DID:
    $ minet bluesky profile-follows did:plc:z72i7hdynmk6r22z27h6tvur --limit 100

. Get follows from profiles by their handles from a CSV file:
    $ minet bluesky profile-follows <handle-column> -i profiles.csv

Tips:

- If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

Note:

- This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky profile-follows "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky profile-follows column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky profile-follows column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky profile-follows column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky profile-follows "value1,value2" --explode ","
```

### profile-followers

```
Usage: minet bluesky profile-followers [-h] [-l LIMIT] [--silent]
                                       [--refresh-per-second REFRESH_PER_SECOND]
                                       [--simple-progress]
                                       [--identifier IDENTIFIER]
                                       [--rcfile RCFILE] [--password PASSWORD]
                                       [-i INPUT] [--explode EXPLODE]
                                       [-s SELECT] [--total TOTAL] [-o OUTPUT]
                                       profile_or_profile_column

# Minet Bluesky Get Followers from Handle or DID command

Get whether followers of a profile giving its handle or DID or respective followers of several profiles given their handle or did from the column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  profile_or_profile_column     Single profile to process or name of the CSV
                                column containing profiles when using
                                -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  -l, --limit LIMIT             Limit the number of followers to retrieve for
                                each profile. Will collect all followers by
                                default.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the profiles you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get followers of a profile by their handle:
    $ minet bluesky profile-followers @bsky.app

. Get 100 followers of a profile by their DID:
    $ minet bluesky profile-followers did:plc:z72i7hdynmk6r22z27h6tvur --limit 100

. Get followers from profiles by their handles from a CSV file:
    $ minet bluesky profile-followers <handle-column> -i profiles.csv

Tips:

- If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

Note:

- This command returns partial user profiles, which can be completed by using the `minet bluesky profiles` command.

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky profile-followers "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky profile-followers column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky profile-followers column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky profile-followers column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky profile-followers "value1,value2" --explode ","
```

### profile-posts

```
Usage: minet bluesky profile-posts [-h] [-l LIMIT] [--silent]
                                   [--refresh-per-second REFRESH_PER_SECOND]
                                   [--simple-progress] [--identifier IDENTIFIER]
                                   [--rcfile RCFILE] [--password PASSWORD]
                                   [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                   [--total TOTAL] [-o OUTPUT]
                                   profile_or_profile_column

# Minet Bluesky Get Profile Posts command

Retrieves Bluesky posts whether by profile using its handle (e.g. @bsky.app) or DID (did:...) or multiple profiles given their handles or DIDs from column of a CSV file. This command uses the Bluesky HTTP API.

Positional Arguments:
  profile_or_profile_column     Single profile to process or name of the CSV
                                column containing profiles when using
                                -i/--input.

Optional Arguments:
  --identifier IDENTIFIER       Bluesky personal identifier (don't forget the
                                `.bsky.social` at the end). Can also be
                                configured in a .minetrc file as
                                "bluesky.identifier" or read from the
                                MINET_BLUESKY_IDENTIFIER env variable.
  -l, --limit LIMIT             Limit the number of posts to retrieve for each
                                profile. Will collect all posts by default.
  --password PASSWORD           Bluesky app password (not your personal
                                password, must be created here:
                                https://bsky.app/settings/app-passwords). Can
                                also be configured in a .minetrc file as
                                "bluesky.password" or read from the
                                MINET_BLUESKY_PASSWORD env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the profiles you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Get posts from a profile by their handle:
    $ minet bluesky profile-posts @bsky.app

. Get 150 last posts from a profile by their DID:
    $ minet bluesky profile-posts did:plc:z72i7hdynmk6r22z27h6tvur --limit 150

. Get posts from profiles by their handles from a CSV file:
    $ minet bluesky profile-posts <handle-column> -i profiles.csv

Tips:

- If you pass the handle, it can be with or without the '@' symbol (e.g. '@bsky.app' or 'bsky.app').

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet bluesky profile-posts "value"

. Here is how to use a command with a CSV file:
    $ minet bluesky profile-posts column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet bluesky profile-posts column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet bluesky profile-posts column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet bluesky profile-posts "value1,value2" --explode ","
```

## Facebook

```
Usage: minet facebook [-h] {experimental-comments,url-likes} ...

# Minet Facebook Command

Collect data from Facebook.

Optional Arguments:
  -h, --help                    show this help message and exit

Subcommands:
  {experimental-comments,url-likes}
                                Subcommand to use.
    experimental-comments       Minet Experimental Facebook Comments Command
    url-likes                   Minet Facebook Url Likes Command
```

### url-likes

```
Usage: minet facebook url-likes [-h] [--silent]
                                [--refresh-per-second REFRESH_PER_SECOND]
                                [--simple-progress] [-i INPUT]
                                [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                                [-o OUTPUT]
                                url_or_url_column

# Minet Facebook Url Likes Command

Retrieve the approximate number of "likes" (actually an aggregated engagement metric)
that a url got on Facebook. The command can also be used with a list of urls stored in a CSV file.
This number is found by scraping Facebook's share button, which only gives a
rough estimation of the real engagement metric: "Share 45K" for example.

Note that this number does not actually only correspond to the number of
likes or shares, but it is rather the sum of like, love, ahah, angry, etc.
reactions plus the number of comments and shares that the URL got on Facebook
(here is the official documentation: https://developers.facebook.com/docs/plugins/faqs
explaining "What makes up the number shown next to my Share button?").

Positional Arguments:
  url_or_url_column             Single url to process or name of the CSV column
                                containing urls when using -i/--input.

Optional Arguments:
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the urls you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:
. Retrieving the "like" number for one url:
    $ minet fb url-likes "www.example-url.com" > url_like.csv

. Retrieving the "like" number for the urls listed in a CSV file:
    $ minet fb url-likes url -i url.csv > url_likes.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet facebook url-likes "value"

. Here is how to use a command with a CSV file:
    $ minet facebook url-likes column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet facebook url-likes column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet facebook url-likes column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet facebook url-likes "value1,value2" --explode ","
```

## Google

```
Usage: minet google [-h] {sheets} ...

# Minet Google Command

Collect data from Google.

Optional Arguments:
  -h, --help  show this help message and exit

Subcommands:
  {sheets}    Subcommand to use.
    sheets    Minet Google Sheets Command
```

### sheets

```
Usage: minet google sheets [-h] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [--simple-progress] [-a AUTHUSER] [-c COOKIE]
                           [-o OUTPUT]
                           url

# Minet Google Sheets Command

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

Positional Arguments:
  url                           Url, sharing url or id of the spreadsheet to
                                export.

Optional Arguments:
  -a, --authuser AUTHUSER       Connected google account number to use.
  -c, --cookie COOKIE           Google Drive cookie or browser from which to
                                extract it (supports "firefox", "chrome",
                                "chromium", "opera" and "edge").
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Exporting from the spreadsheet id:
    $ minet google sheets 1QXQ1yaNYrVUlMt6LQ4jrLGt_PvZI9goozYiBTgaC4RI > file.csv

. Using your Firefox authentication cookies:
    $ minet google sheets --cookie firefox 1QXQ1yaNYrVUlMt6LQ4jrLGt_PvZI9goozYiBTgaC4RI > file.csv
```

## Hyphe

### crawl

```
Usage: minet hyphe crawl [-h] [--silent]
                         [--refresh-per-second REFRESH_PER_SECOND]
                         [--simple-progress] [--id-column ID_COLUMN]
                         [--status-column STATUS_COLUMN]
                         [--prefixes-column PREFIXES_COLUMN]
                         [--prefix-separator PREFIX_SEPARATOR]
                         [--start-pages-column START_PAGES_COLUMN]
                         [--start-page-separator START_PAGE_SEPARATOR]
                         [--ignore-internal-links] [-O OUTPUT_DIR] [--resume]
                         [--max-depth MAX_DEPTH] [--throttle THROTTLE]
                         [--domain-parallelism DOMAIN_PARALLELISM] [-t THREADS]
                         [-z] [--compress-transfer] [-w] [-d]
                         [--folder-strategy FOLDER_STRATEGY]
                         [-f {csv,jsonl,ndjson}] [-v] [-n] [-k] [-p PROCESSES]
                         [--connect-timeout CONNECT_TIMEOUT] [--timeout TIMEOUT]
                         [--retries RETRIES] [--pycurl] [--sqlar]
                         corpus

# Minet Hyphe Crawl Command

Specialized crawl command that can be used to reproduce
a Hyphe crawl from a corpus exported in CSV.

Positional Arguments:
  corpus                        Path to the Hyphe corpus exported to CSV.

Optional Arguments:
  -z, --compress-on-disk        Whether to compress the downloaded files when
                                saving files on disk.
  --compress-transfer           Whether to send a "Accept-Encoding" header
                                asking for a compressed response. Usually better
                                for bandwidth but at the cost of more CPU work.
  --connect-timeout CONNECT_TIMEOUT
                                Maximum socket connection time to host. Defaults
                                to `15`.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to `1`.
  --folder-strategy FOLDER_STRATEGY
                                Name of the strategy to be used to dispatch the
                                retrieved files into folders to alleviate issues
                                on some filesystems when a folder contains too
                                much files. Note that this will be applied on
                                top of --filename-template. All of the
                                strategies are described at the end of this
                                help. Defaults to `fullpath`.
  -f, --format {csv,jsonl,ndjson}
                                Serialization format for scraped/extracted data.
                                Defaults to `csv`.
  --id-column ID_COLUMN         Name of the CSV column containing the webentity
                                ids. Defaults to `ID`.
  --ignore-internal-links       Whether not to write links internal to a
                                webentity on disk.
  -k, --insecure                Whether to allow ssl errors when performing
                                requests or not.
  --max-depth MAX_DEPTH         Maximum depth for the crawl.
  -n, --normalized-url-cache    Whether to normalize url cache used to assess if
                                some url was already visited.
  -O, --output-dir OUTPUT_DIR   Output directory. Defaults to `crawl`.
  --prefix-separator PREFIX_SEPARATOR
                                Separator character for the webentity prefixes.
                                Defaults to ` `.
  --prefixes-column PREFIXES_COLUMN
                                Name of the CSV column containing the webentity
                                prefixes, separated by --prefix-separator.
                                Defaults to `PREFIXES AS URL`.
  -p, --processes PROCESSES     Number of processes for the crawler process
                                pool.
  --pycurl                      Whether to use the pycurl library to perform the
                                calls.
  --retries RETRIES             Number of times to retry on timeout & common
                                network-related issues. Defaults to `3`.
  --sqlar                       Whether to write files into a single-file sqlite
                                archive rather than as individual files on the
                                disk.
  --start-page-separator START_PAGE_SEPARATOR
                                Separator character for the webentity start
                                pages. Defaults to ` `.
  --start-pages-column START_PAGES_COLUMN
                                Name of the CSV column containing the webentity
                                start pages, separated by
                                --start-page-separator. Defaults to `START
                                PAGES`.
  --status-column STATUS_COLUMN
                                Name of the CSV column containing the webentity
                                statuses. Defaults to `STATUS`.
  -t, --threads THREADS         Number of threads to use. Will default to a
                                conservative number, based on the number of
                                available cores. Feel free to increase.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to `0`.
  --timeout TIMEOUT             Maximum time - in seconds - to spend for each
                                request before triggering a timeout. Defaults to
                                `60`.
  -v, --verbose                 Whether to print information about crawl
                                results.
  -d, --write-data, -D, --dont-write-data
                                Whether to write scraped/extracted data on disk.
                                Defaults to `True`.
  -w, --write-files             Whether to write downloaded files on disk in
                                order to save them for later.
  --resume                      Whether to resume an interrupted crawl.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

--folder-strategy options:

. "flat": default choice, all files will be written in the indicated
    content folder.

. "fullpath": all files will be written in a folder consisting of the
    url hostname and then its path.

. "prefix-x": e.g. "prefix-4", files will be written in folders
    having a name that is the first x characters of the file's name.
    This is an efficient way to partition content into folders containing
    roughly the same number of files if the file names are random (which
    is the case by default since md5 hashes will be used).

. "hostname": files will be written in folders based on their url's
    full host name.

. "normalized-hostname": files will be written in folders based on
    their url's hostname stripped of some undesirable parts (such as
    "www.", or "m.", for instance).

. "fingerprinted-hostname": files will be written in folders based on
    their url's hostname stripped of some more undesirable parts (such as
    "fr.", for instance) and their public suffix will be dropped.

Examples:

. Reproducing a crawl:
    $ minet hyphe crawl corpus.csv

Notes regarding sqlite storage temporary files:

If you spawn a persistent crawler, some of its state will be kept using
specialized sqlite databases on disk.

Be aware that sqlite sometimes need to perform cleanup operations that rely
on temporary files that will be written in a folder configured as the
`SQLITE_TMPDIR` env variable. Be sure to set this variable when running this
command, especially when the crawler files will be stored on a different disk
and if writing in the host's `/tmp` directory can be risky due to insufficient
storage available.

For more info, check out: https://www.sqlite.org/tempfiles.html
```

### declare

```
Usage: minet hyphe declare [-h] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [--simple-progress] [--password PASSWORD]
                           [--total TOTAL] [-o OUTPUT]
                           url corpus webentities

# Minet Hyphe Declare Command

Command that can be used to declare series of webentities
in a corpus.

It is ideal to start or restart a corpus using the same exact
webentity declarations as another one.

Positional Arguments:
  url                           Url of the Hyphe API.
  corpus                        Id of the corpus.
  webentities                   CSV file of webentities (exported from Hyphe).

Optional Arguments:
  --password PASSWORD           The corpus's password if required.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Declaring webentities from a Hyphe export:
    $ minet hyphe declare http://myhyphe.com/api/ target-corpus export.csv
```

### destroy

```
Usage: minet hyphe destroy [-h] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [--simple-progress] [--password PASSWORD] [-o OUTPUT]
                           url corpus

# Minet Hyphe Destroy Command

Command that can be used to destroy a corpus entirely.

Positional Arguments:
  url                           Url of the Hyphe API.
  corpus                        Id of the corpus.

Optional Arguments:
  --password PASSWORD           The corpus's password if required.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Destroying a corpus:
    $ minet hyphe destroy http://myhyphe.com/api/ my-corpus
```

### dump

```
Usage: minet hyphe dump [-h] [--silent]
                        [--refresh-per-second REFRESH_PER_SECOND]
                        [--simple-progress] [-O OUTPUT_DIR] [--body]
                        [--statuses STATUSES] [--page-count PAGE_COUNT]
                        [--password PASSWORD] [-o OUTPUT]
                        url corpus

# Minet Hyphe Dump Command

Command dumping page-level information from a given
Hyphe corpus.

Positional Arguments:
  url                           Url of the Hyphe API.
  corpus                        Id of the corpus.

Optional Arguments:
  --body                        Whether to download pages body.
  -O, --output-dir OUTPUT_DIR   Output directory for dumped files. Will default
                                to some name based on corpus name.
  --page-count PAGE_COUNT       Number of pages to download per pagination call.
                                Tweak if corpus has large pages or if the
                                network is unreliable. Defaults to `500`.
  --password PASSWORD           The corpus's password if required.
  --statuses STATUSES           Webentity statuses to dump, separated by comma.
                                Possible statuses being "IN", "OUT", "UNDECIDED"
                                and "DISCOVERED".
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Dumping a corpus into the ./corpus directory:
    $ minet hyphe dump http://myhyphe.com/api/ corpus-name -O corpus
```

### reset

```
Usage: minet hyphe reset [-h] [--silent]
                         [--refresh-per-second REFRESH_PER_SECOND]
                         [--simple-progress] [--password PASSWORD] [-o OUTPUT]
                         url corpus

# Minet Hyphe Reset Command

Command that can be used to reset a corpus entirely.

Positional Arguments:
  url                           Url of the Hyphe API.
  corpus                        Id of the corpus.

Optional Arguments:
  --password PASSWORD           The corpus's password if required.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Resetting a corpus:
    $ minet hyphe reset http://myhyphe.com/api/ my-corpus
```

### tag

```
Usage: minet hyphe tag [-h] [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                       [--simple-progress] [--separator SEPARATOR]
                       [--password PASSWORD] [--total TOTAL] [-o OUTPUT]
                       url corpus webentity_id_column tag_columns data

# Minet Hyphe Tag Command

Command that can be used to tag webentities in batch using
metadata recorded in a CSV file.

Positional Arguments:
  url                           Url of the Hyphe API.
  corpus                        Id of the corpus.
  webentity_id_column           Column of the CSV file containing the webentity
                                ids.
  tag_columns                   Columns, separated by comma, to use as tags.
  data                          CSV file of webentities (exported from Hyphe).

Optional Arguments:
  --password PASSWORD           The corpus's password if required.
  --separator SEPARATOR         Separator use to split multiple tag values in
                                the same column. Defaults to `|`.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Tag webentities from two columns of CSV file:
    $ minet hyphe tag http://myhyphe.com/api/ my-corpus webentity_id type,creator metadata.csv
```

## Instagram

```
Usage: minet instagram [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                       [--refresh-per-second REFRESH_PER_SECOND]
                       [--simple-progress]
                       {comments,hashtag,location,post-infos,user-followers,user-following,user-infos,user-posts}
                       ...

# Minet Instagram Command

Gather data from Instagram.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Subcommands:
  {comments,hashtag,location,post-infos,user-followers,user-following,user-infos,user-posts}
                                Subcommand to use.
    comments                    Instagram Comments Command
    hashtag                     Instagram hashtag
    location                    Instagram location
    post-infos                  Instagram post-infos
    user-followers              Instagram User Followers Command
    user-following              Instagram User Following Command
    user-infos                  Instagram user-infos
    user-posts                  Instagram User Posts Command
```

### comments

```
Usage: minet instagram comments [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                [--refresh-per-second REFRESH_PER_SECOND]
                                [--simple-progress] [-l LIMIT] [-i INPUT]
                                [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                                [-o OUTPUT]
                                post_or_post_column

# Instagram Comments Command

Scrape Instagram comments with a given post url, post shortcode or post id.

This requires to be logged in to an Instagram account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

Positional Arguments:
  post_or_post_column           Single post url, post shortcode or post id to
                                process or name of the CSV column containing
                                post urls, post shortcodes or post ids when
                                using -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  -l, --limit LIMIT             Maximum number of comments to retrieve per post.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the post urls, post shortcodes or post ids you
                                want to process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching comments from the post https://www.instagram.com/p/CpA46rmU26Y/:
    $ minet instagram comments https://www.instagram.com/p/CpA46rmU26Y/ > comments.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet instagram comments "value"

. Here is how to use a command with a CSV file:
    $ minet instagram comments column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet instagram comments column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram comments column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram comments "value1,value2" --explode ","
```

### hashtag

```
Usage: minet instagram hashtag [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [--simple-progress] [-l LIMIT] [-i INPUT]
                               [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                               [-o OUTPUT]
                               hashtag_or_hashtag_column

# Instagram hashtag

Scrape Instagram posts with a given hashtag.

This requires to be logged in to an Instagram account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

display_url is not the media url, but a thumbnail of the post.
There is no way with this command to get the media urls.

Positional Arguments:
  hashtag_or_hashtag_column     Single hashtag to process or name of the CSV
                                column containing hashtags when using
                                -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  -l, --limit LIMIT             Maximum number of posts to retrieve per hashtag.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the hashtags you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching posts with the hashtag paris:
    $ minet instagram hashtag paris > paris_posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet instagram hashtag "value"

. Here is how to use a command with a CSV file:
    $ minet instagram hashtag column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet instagram hashtag column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram hashtag column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram hashtag "value1,value2" --explode ","
```

### location

```
Usage: minet instagram location [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                [--refresh-per-second REFRESH_PER_SECOND]
                                [--simple-progress] [-l LIMIT] [-i INPUT]
                                [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                                [-o OUTPUT]
                                location_or_location_column

# Instagram location

Scrape Instagram posts with a given location id.

This requires to be logged in to an Instagram account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

display_url is not the media url, but a thumbnail of the post.
There is no way with this command to get the media urls.

Positional Arguments:
  location_or_location_column   Single location to process or name of the CSV
                                column containing locations when using
                                -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  -l, --limit LIMIT             Maximum number of posts to retrieve per
                                location.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the locations you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching posts with the location id for Milan, Italy:
    $ minet instagram location 213050058 > 213050058_posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet instagram location "value"

. Here is how to use a command with a CSV file:
    $ minet instagram location column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet instagram location column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram location column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram location "value1,value2" --explode ","
```

### post-infos

```
Usage: minet instagram post-infos [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [--simple-progress] [-i INPUT]
                                  [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [--resume] [-o OUTPUT]
                                  post_or_post_column

# Instagram post-infos

Scrape Instagram infos with a given post url, post shortcode or post id.

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

Positional Arguments:
  post_or_post_column           Single post url, post shortcode or post id to
                                process or name of the CSV column containing
                                post urls, post shortcodes or post ids when
                                using -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the post urls, post shortcodes or post ids you
                                want to process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching infos for the post https://www.instagram.com/p/CpA46rmU26Y/:
    $ minet instagram post-infos https://www.instagram.com/p/CpA46rmU26Y/ > post_infos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet instagram post-infos "value"

. Here is how to use a command with a CSV file:
    $ minet instagram post-infos column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet instagram post-infos column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram post-infos column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram post-infos "value1,value2" --explode ","
```

### user-followers

```
Usage: minet instagram user-followers [-h] [-c COOKIE] [--rcfile RCFILE]
                                      [--silent]
                                      [--refresh-per-second REFRESH_PER_SECOND]
                                      [--simple-progress] [-l LIMIT] [-i INPUT]
                                      [--explode EXPLODE] [-s SELECT]
                                      [--total TOTAL] [-o OUTPUT]
                                      user_or_user_column

# Instagram User Followers Command

Scrape Instagram followers with a given username, user url or user id.
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

If a username is a number without '@' at the beginning, it will be
considered as an id.

Positional Arguments:
  user_or_user_column           Single username, user url or user id to process
                                or name of the CSV column containing usernames,
                                user urls or user ids when using -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  -l, --limit LIMIT             Maximum number of followers to retrieve per
                                user.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the usernames, user urls or user ids you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching followers with the username banksrepeta:
    $ minet instagram user-followers banksrepeta > banksrepeta_followers.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet instagram user-followers "value"

. Here is how to use a command with a CSV file:
    $ minet instagram user-followers column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet instagram user-followers column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram user-followers column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram user-followers "value1,value2" --explode ","
```

### user-following

```
Usage: minet instagram user-following [-h] [-c COOKIE] [--rcfile RCFILE]
                                      [--silent]
                                      [--refresh-per-second REFRESH_PER_SECOND]
                                      [--simple-progress] [-l LIMIT] [-i INPUT]
                                      [--explode EXPLODE] [-s SELECT]
                                      [--total TOTAL] [-o OUTPUT]
                                      user_or_user_column

# Instagram User Following Command

Scrape Instagram accounts followed with a given username, user url or user id.

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

If a username is a number without '@' at the beginning, it will be
considered as an id.

Positional Arguments:
  user_or_user_column           Single username, user url or user id to process
                                or name of the CSV column containing usernames,
                                user urls or user ids when using -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  -l, --limit LIMIT             Maximum number of accounts to retrieve per user.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the usernames, user urls or user ids you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching accounts followed with the username paramountplus:
    $ minet instagram user-following paramountplus > paramountplus_following.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet instagram user-following "value"

. Here is how to use a command with a CSV file:
    $ minet instagram user-following column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet instagram user-following column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram user-following column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram user-following "value1,value2" --explode ","
```

### user-infos

```
Usage: minet instagram user-infos [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [--simple-progress] [-i INPUT]
                                  [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [--resume] [-o OUTPUT]
                                  user_or_user_column

# Instagram user-infos

Scrape Instagram infos with a given username, user url or user id.

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

If a username is a number without '@' at the beginning, it will be
considered as an id.

Positional Arguments:
  user_or_user_column           Single username, user url or user id to process
                                or name of the CSV column containing usernames,
                                user urls or user ids when using -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the usernames, user urls or user ids you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching infos with the username banksrepeta:
    $ minet instagram user-infos banksrepeta > banksrepeta_infos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet instagram user-infos "value"

. Here is how to use a command with a CSV file:
    $ minet instagram user-infos column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet instagram user-infos column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram user-infos column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram user-infos "value1,value2" --explode ","
```

### user-posts

```
Usage: minet instagram user-posts [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [--simple-progress] [-l LIMIT] [-i INPUT]
                                  [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [-o OUTPUT]
                                  user_or_user_column

# Instagram User Posts Command

Scrape Instagram posts with a given username, user url or user id.

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

If a username is a number without '@' at the beginning, it will be
considered as an id.

Positional Arguments:
  user_or_user_column           Single username, user url or user id to process
                                or name of the CSV column containing usernames,
                                user urls or user ids when using -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "instagram.cookie" or read
                                from the MINET_INSTAGRAM_COOKIE env variable.
  -l, --limit LIMIT             Maximum number of posts to retrieve per user.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the usernames, user urls or user ids you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching posts from the account paramountplus:
    $ minet instagram user-posts paramountplus > paramountplus_posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet instagram user-posts "value"

. Here is how to use a command with a CSV file:
    $ minet instagram user-posts column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet instagram user-posts column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram user-posts column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram user-posts "value1,value2" --explode ","
```

## Mediacloud

### medias

```
Usage: minet mediacloud medias [-h] [-t TOKEN] [--rcfile RCFILE] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [--simple-progress] [--feeds FEEDS] [-i INPUT]
                               [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                               [-o OUTPUT]
                               media_or_media_column

# Minet Mediacloud Medias Command

Retrieve metadata about a list of Mediacloud medias.

Positional Arguments:
  media_or_media_column         Single Mediacloud media id to process or name of
                                the CSV column containing Mediacloud media ids
                                when using -i/--input.

Optional Arguments:
  --feeds FEEDS                 If given, path of the CSV file listing media RSS
                                feeds.
  -t, --token TOKEN             Mediacloud API token (also called "key"
                                sometimes). Can also be configured in a .minetrc
                                file as "mediacloud.token" or read from the
                                MINET_MEDIACLOUD_TOKEN env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the Mediacloud media ids you want to process.
                                Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet mediacloud medias "value"

. Here is how to use a command with a CSV file:
    $ minet mediacloud medias column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet mediacloud medias column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet mediacloud medias column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet mediacloud medias "value1,value2" --explode ","
```

### search

```
Usage: minet mediacloud search [-h] [-t TOKEN] [--rcfile RCFILE] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [--simple-progress] [-c COLLECTIONS]
                               [--filter-query FILTER_QUERY] [-m MEDIAS]
                               [--publish-day PUBLISH_DAY]
                               [--publish-month PUBLISH_MONTH]
                               [--publish-year PUBLISH_YEAR] [--skip-count]
                               [-o OUTPUT]
                               query

# Minet Mediacloud Search Command

Search stories on the Mediacloud platform.

To learn how to compose more relevant queries, check out this guide:
https://mediacloud.org/support/query-guide

Positional Arguments:
  query                         Search query.

Optional Arguments:
  -c, --collections COLLECTIONS
                                List of collection ids to search, separated by
                                commas.
  --filter-query FILTER_QUERY   Solr filter query `fq` to use. Can be used to
                                optimize some parts of the query.
  -m, --medias MEDIAS           List of media ids to search, separated by
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
  -t, --token TOKEN             Mediacloud API token (also called "key"
                                sometimes). Can also be configured in a .minetrc
                                file as "mediacloud.token" or read from the
                                MINET_MEDIACLOUD_TOKEN env variable.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit
```

### topic

#### stories

```
Usage: minet mediacloud topic stories [-h] [-t TOKEN] [--rcfile RCFILE]
                                      [--silent]
                                      [--refresh-per-second REFRESH_PER_SECOND]
                                      [--simple-progress] [--media-id MEDIA_ID]
                                      [--from-media-id FROM_MEDIA_ID]
                                      [-o OUTPUT]
                                      topic_id

# Minet Mediacloud Topic Stories Command

Retrieves the list of stories from a mediacloud topic.

Positional Arguments:
  topic_id                      Id of the topic.

Optional Arguments:
  --from-media-id FROM_MEDIA_ID
                                Return only stories that are linked from stories
                                in the given media_id.
  --media-id MEDIA_ID           Return only stories belonging to the given
                                media_ids.
  -t, --token TOKEN             Mediacloud API token (also called "key"
                                sometimes). Can also be configured in a .minetrc
                                file as "mediacloud.token" or read from the
                                MINET_MEDIACLOUD_TOKEN env variable.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit
```

## Reddit

```
Usage: minet reddit [-h] {posts,comments,user-posts,user-comments} ...

# Minet Reddit Command

Collect data from Reddit.

Optional Arguments:
  -h, --help                    show this help message and exit

Subcommands:
  {posts,comments,user-posts,user-comments}
                                Subcommand to use.
    posts                       Minet Reddit Posts Command
    comments                    Minet Reddit Comments Command
    user-posts                  Minet Reddit User Posts Command
    user-comments               Minet Reddit User Comments Command
```

### comments

```
Usage: minet reddit comments [-h] [-A] [--silent]
                             [--refresh-per-second REFRESH_PER_SECOND]
                             [--simple-progress] [-i INPUT] [--explode EXPLODE]
                             [-s SELECT] [--total TOTAL] [-o OUTPUT]
                             post_or_post_column

# Minet Reddit Comments Command

Retrieve comments from a reddit post link.
Note that it will only retrieve the comments displayed on the page. If you want all the comments you need to use -A, --all but it will require a request per comment, and you can only make 100 requests per 10 minutes.

Positional Arguments:
  post_or_post_column           Single post url, shortcode or id to process or
                                name of the CSV column containing posts urls,
                                shortcodes or ids when using -i/--input.

Optional Arguments:
  -A, --all                     Retrieve all comments.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the posts urls, shortcodes or ids you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching comments from a reddit post:
    $ minet reddit comments https://www.reddit.com/r/france/comments/... > r_france_comments.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet reddit comments "value"

. Here is how to use a command with a CSV file:
    $ minet reddit comments column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet reddit comments column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet reddit comments column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet reddit comments "value1,value2" --explode ","
```

### posts

```
Usage: minet reddit posts [-h] [-l LIMIT] [--silent]
                          [--refresh-per-second REFRESH_PER_SECOND]
                          [--simple-progress] [-t] [-i INPUT]
                          [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                          [-o OUTPUT]
                          subreddit_or_subreddit_column

# Minet Reddit Posts Command

Retrieve reddit posts from a subreddit link or name.

Positional Arguments:
  subreddit_or_subreddit_column
                                Single subreddit url, shortcode or id to process
                                or name of the CSV column containing subreddit
                                urls, shortcodes or ids when using -i/--input.

Optional Arguments:
  -l, --limit LIMIT             Maximum number of posts to retrieve.
  -t, --text                    Retrieve the text of the post. Note that it will
                                require one request per post.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the subreddit urls, shortcodes or ids you want
                                to process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching posts from the subreddit r/france:
    $ minet reddit posts https://www.reddit.com/r/france > r_france_posts.csv
    $ minet reddit posts france > r_france_posts.csv
    $ minet reddit posts r/france > r_france_posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet reddit posts "value"

. Here is how to use a command with a CSV file:
    $ minet reddit posts column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet reddit posts column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet reddit posts column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet reddit posts "value1,value2" --explode ","
```

### user-comments

```
Usage: minet reddit user-comments [-h] [-l LIMIT] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [--simple-progress] [-i INPUT]
                                  [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [-o OUTPUT]
                                  user_or_user_column

# Minet Reddit User Comments Command

Retrieve reddit comments from a user link.

Positional Arguments:
  user_or_user_column           Single user url, shortcode or id to process or
                                name of the CSV column containing user urls,
                                shortcodes or ids when using -i/--input.

Optional Arguments:
  -l, --limit LIMIT             Maximum number of comments to retrieve.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the user urls, shortcodes or ids you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching comments from the user page of u/reddit:
    $ minet reddit user-comments https://www.reddit.com/user/reddit/comments/ > reddit_comments.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet reddit user-comments "value"

. Here is how to use a command with a CSV file:
    $ minet reddit user-comments column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet reddit user-comments column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet reddit user-comments column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet reddit user-comments "value1,value2" --explode ","
```

### user-posts

```
Usage: minet reddit user-posts [-h] [-l LIMIT] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [--simple-progress] [-t] [-i INPUT]
                               [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                               [-o OUTPUT]
                               user_or_user_column

# Minet Reddit User Posts Command

Retrieve reddit posts from a user link.

Positional Arguments:
  user_or_user_column           Single user url, shortcode or id to process or
                                name of the CSV column containing user urls,
                                shortcodes or ids when using -i/--input.

Optional Arguments:
  -l, --limit LIMIT             Maximum number of posts to retrieve.
  -t, --text                    Retrieve the text of the post. Note that it will
                                require one request per post.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the user urls, shortcodes or ids you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching posts from the user page of u/reddit:
    $ minet reddit user-posts https://www.reddit.com/user/reddit/submitted/ > reddit_posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet reddit user-posts "value"

. Here is how to use a command with a CSV file:
    $ minet reddit user-posts column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet reddit user-posts column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet reddit user-posts column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet reddit user-posts "value1,value2" --explode ","
```

## Telegram

### channel-infos

```
Usage: minet telegram channel-infos [-h] [--throttle THROTTLE] [--silent]
                                    [--refresh-per-second REFRESH_PER_SECOND]
                                    [--simple-progress] [-i INPUT]
                                    [--explode EXPLODE] [-s SELECT]
                                    [--total TOTAL] [-o OUTPUT]
                                    channel_name_or_channel_name_column

# Minet Telegram Channel-Infos Command

Scrape a Telegram channel's infos.

Positional Arguments:
  channel_name_or_channel_name_column
                                Single channel name / url to process or name of
                                the CSV column containing channel names / urls
                                when using -i/--input.

Optional Arguments:
  --throttle THROTTLE           Throttling time, in seconds, to wait between
                                each request. Defaults to `0.5`.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the channel names / urls you want to process.
                                Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:
. Scraping a channel's infos:
    $ minet telegram channel-infos nytimes > infos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet telegram channel-infos "value"

. Here is how to use a command with a CSV file:
    $ minet telegram channel-infos column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet telegram channel-infos column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet telegram channel-infos column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet telegram channel-infos "value1,value2" --explode ","
```

### channel-messages

```
Usage: minet telegram channel-messages [-h] [--throttle THROTTLE] [--silent]
                                       [--refresh-per-second REFRESH_PER_SECOND]
                                       [--simple-progress] [--desc] [-i INPUT]
                                       [--explode EXPLODE] [-s SELECT]
                                       [--total TOTAL] [-o OUTPUT]
                                       channel_name_or_channel_name_column

# Minet Telegram Channel-Messages Command

Scrape Telegram channel messages.

Positional Arguments:
  channel_name_or_channel_name_column
                                Single channel name / url to process or name of
                                the CSV column containing channel names / urls
                                when using -i/--input.

Optional Arguments:
  --desc                        Whether to collect data in reverse chronological
                                order instead of default chronological order.
  --throttle THROTTLE           Throttling time, in seconds, to wait between
                                each request. Defaults to `0.5`.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the channel names / urls you want to process.
                                Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:
. Scraping a group's posts:
    $ minet telegram channel-messages nytimes > messages.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet telegram channel-messages "value"

. Here is how to use a command with a CSV file:
    $ minet telegram channel-messages column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet telegram channel-messages column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet telegram channel-messages column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet telegram channel-messages "value1,value2" --explode ","
```

## Tiktok

```
Usage: minet tiktok [-h]
                    {search-videos,search-commercials,scrape-commercials} ...

# Minet Tiktok Command

Gather data from Tiktok.

Optional Arguments:
  -h, --help                    show this help message and exit

Subcommands:
  {search-videos,search-commercials,scrape-commercials}
                                Subcommand to use.
    search-videos               Tiktok Search Videos Command
    search-commercials          Tiktok Search Commercial Contents Command
    scrape-commercials          Tiktok Scrape Commercial Contents Command
```

### scrape-commercials

```
Usage: minet tiktok scrape-commercials [-h] [-c COUNTRY] [--silent]
                                       [--refresh-per-second REFRESH_PER_SECOND]
                                       [--simple-progress] [--min-date MIN_DATE]
                                       [--max-date MAX_DATE] [-t TOTAL]
                                       [--key KEY] [--rcfile RCFILE]
                                       [--secret SECRET] [-o OUTPUT]

# Tiktok Scrape Commercial Contents Command

Query Tiktok commercial contents from the Ad Library website.

Optional Arguments:
  -c, --country COUNTRY         The country of the commercial content's author.
                                Defaults to `all`.
  --key KEY                     Tiktok API identification key. Can also be
                                configured in a .minetrc file as
                                "tiktok.api_key" or read from the
                                MINET_TIKTOK_API_KEY env variable.
  --max-date MAX_DATE           The end of the time range during which the
                                commercial contents were published. Defaults to
                                `2025-12-02`.
  --min-date MIN_DATE           Needs to be after October 1st, 2022. Defaults to
                                `2022-10-01`.
  --secret SECRET               Tiktok API identification secret. Can also be
                                configured in a .minetrc file as
                                "tiktok.api_secret" or read from the
                                MINET_TIKTOK_API_SECRET env variable.
  -t, --total TOTAL             Maximum number of contents to retrieve in total.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching commercial contents from October 1st 2024 00:00:00 to October 2nd 2024 12:00:00 in Romania:
    $ minet tiktok scrape-commercials --country RO --min-date 2024-10-01 --max-date 2024-10-02T12:00:00 > romania.csv
```

### search-commercials

```
Usage: minet tiktok search-commercials [-h] [-c COUNTRY] [--silent]
                                       [--refresh-per-second REFRESH_PER_SECOND]
                                       [--simple-progress] [--min-date MIN_DATE]
                                       [--max-date MAX_DATE] [-t TOTAL]
                                       [--key KEY] [--rcfile RCFILE]
                                       [--secret SECRET] [-o OUTPUT]

# Tiktok Search Commercial Contents Command

Query Tiktok commercial contents using the Ad Library API.

Optional Arguments:
  -c, --country COUNTRY         The country of the commercial content's author.
                                Defaults to `ALL`.
  --key KEY                     Tiktok API identification key. Can also be
                                configured in a .minetrc file as
                                "tiktok.api_key" or read from the
                                MINET_TIKTOK_API_KEY env variable.
  --max-date MAX_DATE           The end of the time range during which the
                                commercial contents were published. Defaults to
                                `20251201`.
  --min-date MIN_DATE           Needs to be after October 1st, 2022. Defaults to
                                `20221001`.
  --secret SECRET               Tiktok API identification secret. Can also be
                                configured in a .minetrc file as
                                "tiktok.api_secret" or read from the
                                MINET_TIKTOK_API_SECRET env variable.
  -t, --total TOTAL             Maximum number of contents to retrieve in total.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching all commercial contents published in Romania from October 1st to October 2nd 2024:
    $ minet tiktok search-commercials --country RO --min-date 20241001 --max-date 20241002 > romania.csv
```

### search-videos

```
Usage: minet tiktok search-videos [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [--simple-progress] [-l LIMIT] [-i INPUT]
                                  [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [-o OUTPUT]
                                  query_or_query_column

# Tiktok Search Videos Command

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

Positional Arguments:
  query_or_query_column         Single tiktok keyword to process or name of the
                                CSV column containing tiktok keywords when using
                                -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "tiktok.cookie" or read from
                                the MINET_TIKTOK_COOKIE env variable.
  -l, --limit LIMIT             Maximum number of videos to retrieve per query.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the tiktok keywords you want to process. Will
                                consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Example:

. Searching videos with the keyword paris:
    $ minet tiktok search-videos paris > paris_videos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet tiktok search-videos "value"

. Here is how to use a command with a CSV file:
    $ minet tiktok search-videos column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet tiktok search-videos column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet tiktok search-videos column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet tiktok search-videos "value1,value2" --explode ","
```

## Twitter

### attrition

```
Usage: minet twitter attrition [-h] [--user USER] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [--simple-progress] [--retweeted-id RETWEETED_ID]
                               [--ids] [--api-key API_KEY] [--rcfile RCFILE]
                               [--api-secret-key API_SECRET_KEY]
                               [--access-token ACCESS_TOKEN]
                               [--access-token-secret ACCESS_TOKEN_SECRET]
                               [-i INPUT] [--explode EXPLODE] [-s SELECT]
                               [--total TOTAL] [--resume] [-o OUTPUT]
                               tweet_url_or_id_or_tweet_url_or_id_column

# Minet Twitter Attrition Command

Using Twitter API to find whether batches of tweets are still
available today and if they aren't, attempt to find a reason why.

This command relies on tweet ids or tweet urls. We recommend to add `--user` and
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

Positional Arguments:
  tweet_url_or_id_or_tweet_url_or_id_column
                                Single tweet url or id to process or name of the
                                CSV column containing tweet urls or ids when
                                using -i/--input.

Optional Arguments:
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
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the tweet urls or ids you want to process. Will
                                consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Finding out if tweets in a CSV files are still available or not using tweet ids:
    $ minet tw attrition tweet_url -i deleted_tweets.csv > attrition-report.csv

. Finding out if tweets are still available or not using tweet & user ids:
    $ minet tw attrition tweet_id -i deleted_tweets.csv --user user_id --ids > attrition-report.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter attrition "value"

. Here is how to use a command with a CSV file:
    $ minet twitter attrition column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter attrition column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter attrition column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter attrition "value1,value2" --explode ","
```

### followers

```
Usage: minet twitter followers [-h] [--ids] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [--simple-progress] [--v2] [--api-key API_KEY]
                               [--rcfile RCFILE]
                               [--api-secret-key API_SECRET_KEY]
                               [--access-token ACCESS_TOKEN]
                               [--access-token-secret ACCESS_TOKEN_SECRET]
                               [-i INPUT] [--explode EXPLODE] [-s SELECT]
                               [--total TOTAL] [--resume] [-o OUTPUT]
                               user_or_user_column

# Minet Twitter Followers Command

Retrieve followers, i.e. followed users, of given user.

Positional Arguments:
  user_or_user_column           Single Twitter account screen name or id to
                                process or name of the CSV column containing
                                Twitter account screen names or ids when using
                                -i/--input.

Optional Arguments:
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
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the Twitter account screen names or ids you want
                                to process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Getting followers of a list of user:
    $ minet tw followers screen_name -i users.csv > followers.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter followers "value"

. Here is how to use a command with a CSV file:
    $ minet twitter followers column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter followers column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter followers column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter followers "value1,value2" --explode ","
```

### followers-you-know

```
Usage: minet twitter followers-you-know [-h] [-c COOKIE] [--rcfile RCFILE]
                                        [--silent]
                                        [--refresh-per-second REFRESH_PER_SECOND]
                                        [--simple-progress]
                                        [--timezone TIMEZONE] [-i INPUT]
                                        [--explode EXPLODE] [-s SELECT]
                                        [--total TOTAL] [-o OUTPUT]
                                        user_id_or_user_id_column

# Minet Twitter Followers You Know Command

Scrape Twitter's public facing "followers you know" lists such
as the one shown here on the website:
https://twitter.com/DEFACTO_UE/followers_you_follow

Note that this command only work when you provide user ids, as
providing screen names will not work.

Be aware that follower lists on Twitter currently are known
to be inconsistent when the actual number of users is roughly
over 50.

Positional Arguments:
  user_id_or_user_id_column     Single user_id to process or name of the CSV
                                column containing user ids when using
                                -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "twitter.cookie" or read from
                                the MINET_TWITTER_COOKIE env variable.
  --timezone TIMEZONE           Timezone for dates, for example 'Europe/Paris'.
                                Defaults to UTC.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the user ids you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Collecting the followers you know from some user id:
    $ minet tw followers-you-know 794083798912827393 > users.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter followers-you-know "value"

. Here is how to use a command with a CSV file:
    $ minet twitter followers-you-know column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter followers-you-know column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter followers-you-know column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter followers-you-know "value1,value2" --explode ","
```

### friends

```
Usage: minet twitter friends [-h] [--ids] [--silent]
                             [--refresh-per-second REFRESH_PER_SECOND]
                             [--simple-progress] [--v2] [--api-key API_KEY]
                             [--rcfile RCFILE] [--api-secret-key API_SECRET_KEY]
                             [--access-token ACCESS_TOKEN]
                             [--access-token-secret ACCESS_TOKEN_SECRET]
                             [-i INPUT] [--explode EXPLODE] [-s SELECT]
                             [--total TOTAL] [--resume] [-o OUTPUT]
                             user_or_user_column

# Minet Twitter Friends Command

Retrieve friends, i.e. followed users, of given user.

Positional Arguments:
  user_or_user_column           Single Twitter account screen name or id to
                                process or name of the CSV column containing
                                Twitter account screen names or ids when using
                                -i/--input.

Optional Arguments:
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
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the Twitter account screen names or ids you want
                                to process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Getting friends of a list of user:
    $ minet tw friends screen_name -i users.csv > friends.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter friends "value"

. Here is how to use a command with a CSV file:
    $ minet twitter friends column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter friends column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter friends column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter friends "value1,value2" --explode ","
```

### list-followers

```
Usage: minet twitter list-followers [-h] [--api-key API_KEY] [--rcfile RCFILE]
                                    [--silent]
                                    [--refresh-per-second REFRESH_PER_SECOND]
                                    [--simple-progress]
                                    [--api-secret-key API_SECRET_KEY]
                                    [--access-token ACCESS_TOKEN]
                                    [--access-token-secret ACCESS_TOKEN_SECRET]
                                    [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                    [--total TOTAL] [-o OUTPUT]
                                    list_or_list_column

# Minet Twitter List Followers Command

Retrieve followers of given list using Twitter API v2.

Positional Arguments:
  list_or_list_column           Single Twitter list id or url to process or name
                                of the CSV column containing Twitter list ids or
                                urls when using -i/--input.

Optional Arguments:
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
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the Twitter list ids or urls you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Getting followers of a list of lists:
    $ minet tw list-followers id -i lists.csv > followers.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter list-followers "value"

. Here is how to use a command with a CSV file:
    $ minet twitter list-followers column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter list-followers column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter list-followers column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter list-followers "value1,value2" --explode ","
```

### list-members

```
Usage: minet twitter list-members [-h] [--api-key API_KEY] [--rcfile RCFILE]
                                  [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [--simple-progress]
                                  [--api-secret-key API_SECRET_KEY]
                                  [--access-token ACCESS_TOKEN]
                                  [--access-token-secret ACCESS_TOKEN_SECRET]
                                  [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [-o OUTPUT]
                                  list_or_list_column

# Minet Twitter List Members Command

Retrieve members of given list using Twitter API v2.

Positional Arguments:
  list_or_list_column           Single Twitter list id or url to process or name
                                of the CSV column containing Twitter list ids or
                                urls when using -i/--input.

Optional Arguments:
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
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the Twitter list ids or urls you want to
                                process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Getting members of a list of lists:
    $ minet tw list-members id -i lists.csv > members.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter list-members "value"

. Here is how to use a command with a CSV file:
    $ minet twitter list-members column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter list-members column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter list-members column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter list-members "value1,value2" --explode ","
```

### retweeters

```
Usage: minet twitter retweeters [-h] [--timezone TIMEZONE] [--silent]
                                [--refresh-per-second REFRESH_PER_SECOND]
                                [--simple-progress] [--api-key API_KEY]
                                [--rcfile RCFILE]
                                [--api-secret-key API_SECRET_KEY]
                                [--access-token ACCESS_TOKEN]
                                [--access-token-secret ACCESS_TOKEN_SECRET]
                                [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                [--total TOTAL] [-o OUTPUT]
                                tweet_id_or_tweet_id_column

# Minet Twitter Retweeters Command

Retrieve retweeters of given tweet using Twitter API v2.

Positional Arguments:
  tweet_id_or_tweet_id_column   Single tweet id to process or name of the CSV
                                column containing tweet ids when using
                                -i/--input.

Optional Arguments:
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
  --timezone TIMEZONE           Timezone for dates, for example 'Europe/Paris'.
                                Defaults to UTC.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the tweet ids you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Getting the users who retweeted a list of tweets:
    $ minet tw retweeters tweet_id -i tweets.csv > retweeters.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter retweeters "value"

. Here is how to use a command with a CSV file:
    $ minet twitter retweeters column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter retweeters column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter retweeters column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter retweeters "value1,value2" --explode ","
```

### scrape

```
Usage: minet twitter scrape [-h] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [--simple-progress] [--include-refs] [-l LIMIT]
                            [--query-template QUERY_TEMPLATE] [-c COOKIE]
                            [--rcfile RCFILE] [-f] [--timezone TIMEZONE]
                            [-i INPUT] [--explode EXPLODE] [-s SELECT]
                            [--total TOTAL] [-o OUTPUT]
                            {tweets,users} query_or_query_column

# Minet Twitter Scrape Command

Scrape Twitter's public facing search API to collect tweets or users.

Be sure to check Twitter's advanced search to check what kind of
operators you can use to tune your queries (time range, hashtags,
mentions, boolean etc.):
https://twitter.com/search-advanced?f=live

Useful operators include "since" and "until" to search specific
time ranges like so: "since:2014-01-01 until:2017-12-31", or "from" that
let you search all tweets from a given user like so: "from:medialab_ScPo".

Note that since 2023-04-21, Twitter search is not available to
visitors of the website without being logged in. This means that
the scraper now requires some cookies to be able to work. So, by
default, the command will grab the relevant cookies from your
local Firefox browser (be sure to be logged in). But you can also
ask the command to grab the cookie from another browser or provide
the cookie string directly instead. Check the -c/--cookie docs to
figure out how to proceed.

Finally, be advised that since you are actually using your account
to scrape data, there is nothing preventing Twitter from banning your
account and it might very well happen in the future (who knows?).

BEWARE: the web search results seem to become inconsistent when
queries return vast amounts of tweets. In which case you are
strongly advised to segment your queries using temporal filters.

NOTE 2023-07-12: scraping users does not work anymore for now.
Tweet scraping was fixed but He-Who-Must-Not-Be-Named breaks things
on a daily basis so be warned this might not be very stable nor
consistent.

Positional Arguments:
  {tweets,users}                What to scrape. Currently only allows for
                                `tweets` or `users`.
  query_or_query_column         Single query to process or name of the CSV
                                column containing queries when using -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "twitter.cookie" or read from
                                the MINET_TWITTER_COOKIE env variable.
  -f, --force                   Bypass confirmation.
  --include-refs                Whether to emit referenced tweets (quoted,
                                retweeted & replied) in the CSV output. Note
                                that it consumes a memory proportional to the
                                total number of unique tweets retrieved.
  -l, --limit LIMIT             Maximum number of tweets or users to collect per
                                query.
  --query-template QUERY_TEMPLATE
                                Query template. Can be useful for instance to
                                change a column of twitter user screen names
                                into from:@user queries.
  --timezone TIMEZONE           Timezone for dates, for example 'Europe/Paris'.
                                Defaults to UTC.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the queries you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Collecting the latest 500 tweets of a given Twitter user:
    $ minet tw scrape tweets "from:@jack" --limit 500 > tweets.csv

. Collecting the tweets from multiple Twitter queries listed in a CSV file:
    $ minet tw scrape tweets query -i queries.csv > tweets.csv

. Templating the given CSV column to query tweets by users:
    $ minet tw scrape tweets user -i users.csv --query-template 'from:@{value}' > tweets.csv

. Collecting users with "adam" in their user_name or user_description:
    $ minet tw scrape users adam > users.csv

Tips:

- You can add a "OR @aNotExistingHandle" to your query to avoid searching
  for your query terms in usernames or handles. Note that this is a temporary hack
  which might stop working at any time so be sure to double check before relying on
  this trick.

    $ minet tw scrape tweets "keyword OR @anObviouslyNotExistingHandle"

  For more information see the related discussion here:
  https://webapps.stackexchange.com/questions/127425/how-to-exclude-usernames-and-handles-while-searching-twitter

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter scrape "value"

. Here is how to use a command with a CSV file:
    $ minet twitter scrape column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter scrape column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter scrape column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter scrape "value1,value2" --explode ","
```

### tweet-date

```
Usage: minet twitter tweet-date [-h] [--timezone TIMEZONE] [--silent]
                                [--refresh-per-second REFRESH_PER_SECOND]
                                [--simple-progress] [-i INPUT]
                                [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                                [-o OUTPUT]
                                tweet_or_tweet_column

# Minet Twitter Tweet Date Command

Getting timestamp and date from tweet url or id.

Positional Arguments:
  tweet_or_tweet_column         Single tweet url or id to process or name of the
                                CSV column containing tweet urls or ids when
                                using -i/--input.

Optional Arguments:
  --timezone TIMEZONE           Timezone for dates, for example 'Europe/Paris'.
                                Defaults to UTC.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the tweet urls or ids you want to process. Will
                                consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

    $ minet tw tweet-date url -i tweets.csv --timezone 'Europe/Paris'> tweets_timestamp_date.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter tweet-date "value"

. Here is how to use a command with a CSV file:
    $ minet twitter tweet-date column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter tweet-date column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter tweet-date column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter tweet-date "value1,value2" --explode ","
```

### tweet-search

```
Usage: minet twitter tweet-search [-h] [--since-id SINCE_ID] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [--simple-progress] [--until-id UNTIL_ID]
                                  [--start-time START_TIME]
                                  [--end-time END_TIME] [--academic]
                                  [--timezone TIMEZONE]
                                  [--sort-order {recency,relevancy}]
                                  [--api-key API_KEY] [--rcfile RCFILE]
                                  [--api-secret-key API_SECRET_KEY]
                                  [--access-token ACCESS_TOKEN]
                                  [--access-token-secret ACCESS_TOKEN_SECRET]
                                  [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [-o OUTPUT]
                                  query_or_query_column

# Minet Twitter Tweets Search Command

Search Twitter tweets using API v2.

This will only return the last 8 days of results maximum per query (unless you have Academic Research access).

To search the full archive of public tweets, use --academic if you have academic research access.

Positional Arguments:
  query_or_query_column         Single query to process or name of the CSV
                                column containing queries when using -i/--input.

Optional Arguments:
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
  --end-time END_TIME           The newest UTC datetime from which the tweets
                                will be counted. The date should have the
                                format: "YYYY-MM-DDTHH:mm:ssZ" but incomplete
                                dates will be completed for you e.g. "2002-04".
  --since-id SINCE_ID           Will return tweets with ids that are greater
                                than the specified id. Takes precedence over
                                --start-time.
  --sort-order {recency,relevancy}
                                How to sort retrieved tweets. Defaults to
                                `recency`.
  --start-time START_TIME       The oldest UTC datetime from which the tweets
                                will be counted. The date should have the
                                format: "YYYY-MM-DDTHH:mm:ssZ" but incomplete
                                dates will be completed for you e.g. "2002-04".
  --timezone TIMEZONE           Timezone for dates, for example 'Europe/Paris'.
                                Defaults to UTC.
  --until-id UNTIL_ID           Will return tweets that are older than the tweet
                                with the specified id.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the queries you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Searching tweets using "cancer" as a query:
    $ minet tw tweet-search cancer > tweets.csv

. Running multiple queries in series:
    $ minet tw tweet-search query -i queries.csv > tweets.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter tweet-search "value"

. Here is how to use a command with a CSV file:
    $ minet twitter tweet-search column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter tweet-search column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter tweet-search column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter tweet-search "value1,value2" --explode ","
```

### tweet-count

```
Usage: minet twitter tweet-count [-h] [--granularity {day,hour,minute}]
                                 [--silent]
                                 [--refresh-per-second REFRESH_PER_SECOND]
                                 [--simple-progress] [--since-id SINCE_ID]
                                 [--until-id UNTIL_ID] [--start-time START_TIME]
                                 [--end-time END_TIME] [--academic]
                                 [--api-key API_KEY] [--rcfile RCFILE]
                                 [--api-secret-key API_SECRET_KEY]
                                 [--access-token ACCESS_TOKEN]
                                 [--access-token-secret ACCESS_TOKEN_SECRET]
                                 [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                 [--total TOTAL] [-o OUTPUT]
                                 query_or_query_column

# Minet Twitter Tweets Count Command

Count the number of tweets matching a given query using
Twitter API v2.

The counts can be granularized by day, hour or minute.

The API is also meant to return the total number of tweets
matching the query but this has been found to be unreliable
and inconsistent so you will have to sum the granularized
counts instead.

The current command does not aggregate per month or year
because sometimes the order of counts does not seem
to be reliable either (even if they are found to be complete
in the final output).

Note that if you don't have an academic access, this command
will only return counts for the last ~7 days only.

If you have an academic access, don't forget to use the
--academic flag.

Finally note that sometimes, the API returns no data instead
of counts of 0, in which case no lines will be emitted in
the CSV output for the affected query.

API docs for the relevant call:
https://developer.twitter.com/en/docs/twitter-api/tweets/counts/api-reference/get-tweets-counts-recent

API docs for the academic call:
https://developer.twitter.com/en/docs/twitter-api/tweets/counts/api-reference/get-tweets-counts-all

Positional Arguments:
  query_or_query_column         Single query to process or name of the CSV
                                column containing queries when using -i/--input.

Optional Arguments:
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
  --end-time END_TIME           The newest UTC datetime from which the tweets
                                will be counted. The date should have the
                                format: "YYYY-MM-DDTHH:mm:ssZ" but incomplete
                                dates will be completed for you e.g. "2002-04".
  --granularity {day,hour,minute}
                                Granularity used to group the data by. Defaults
                                to `day`.
  --since-id SINCE_ID           Will return tweets with ids that are greater
                                than the specified id. Takes precedence over
                                --start-time.
  --start-time START_TIME       The oldest UTC datetime from which the tweets
                                will be counted. The date should have the
                                format: "YYYY-MM-DDTHH:mm:ssZ" but incomplete
                                dates will be completed for you e.g. "2002-04".
  --until-id UNTIL_ID           Will return tweets that are older than the tweet
                                with the specified id.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the queries you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Counting tweets using "cancer" as a query:
    $ minet tw tweet-count cancer

. Running multiple queries in series:
    $ minet tw tweet-count query -i queries.csv > counts.csv

. Number of tweets matching the query per day:
    $ minet tw tweet-count "query" --granularity day > counts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter tweet-count "value"

. Here is how to use a command with a CSV file:
    $ minet twitter tweet-count column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter tweet-count column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter tweet-count column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter tweet-count "value1,value2" --explode ","
```

### tweets

```
Usage: minet twitter tweets [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [--simple-progress] [-f] [-i INPUT]
                            [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                            [--resume] [-o OUTPUT]
                            tweet_id_or_tweet_id_column

# Minet Twitter Tweets Command

Collecting tweet metadata by scraping the website.

Positional Arguments:
  tweet_id_or_tweet_id_column   Single tweet id to process or name of the CSV
                                column containing tweet ids when using
                                -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "twitter.cookie" or read from
                                the MINET_TWITTER_COOKIE env variable.
  -f, --force                   Bypass confirmation.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the tweet ids you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Getting metadata from tweets in a CSV file:
    $ minet tw tweets tweet_id -i tweets.csv > tweets_metadata.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter tweets "value"

. Here is how to use a command with a CSV file:
    $ minet twitter tweets column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter tweets column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter tweets column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter tweets "value1,value2" --explode ","
```

### users

```
Usage: minet twitter users [-h] [--ids] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [--simple-progress] [--v2] [--timezone TIMEZONE]
                           [--api-key API_KEY] [--rcfile RCFILE]
                           [--api-secret-key API_SECRET_KEY]
                           [--access-token ACCESS_TOKEN]
                           [--access-token-secret ACCESS_TOKEN_SECRET]
                           [-i INPUT] [--explode EXPLODE] [-s SELECT]
                           [--total TOTAL] [--resume] [-o OUTPUT]
                           user_or_user_column

# Minet Twitter Users Command

Retrieve Twitter user metadata using the API.

Positional Arguments:
  user_or_user_column           Single Twitter user to process or name of the
                                CSV column containing Twitter users when using
                                -i/--input.

Optional Arguments:
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
  --timezone TIMEZONE           Timezone for dates, for example 'Europe/Paris'.
                                Defaults to UTC.
  --v2                          Whether to use latest Twitter API v2 rather than
                                v1.1.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the Twitter users you want to process. Will
                                consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Getting friends of a list of user:
    $ minet tw users screen_name -i users.csv > data_users.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter users "value"

. Here is how to use a command with a CSV file:
    $ minet twitter users column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter users column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter users column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter users "value1,value2" --explode ","
```

### user-search

```
Usage: minet twitter user-search [-h] [--timezone TIMEZONE] [--silent]
                                 [--refresh-per-second REFRESH_PER_SECOND]
                                 [--simple-progress] [--api-key API_KEY]
                                 [--rcfile RCFILE]
                                 [--api-secret-key API_SECRET_KEY]
                                 [--access-token ACCESS_TOKEN]
                                 [--access-token-secret ACCESS_TOKEN_SECRET]
                                 [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                 [--total TOTAL] [-o OUTPUT]
                                 query_or_query_column

# Minet Twitter Users Search Command

Search Twitter users using API v1.

This will only return ~1000 results maximum per query
so you might want to find a way to segment your inquiry
into smaller queries to find more users.

Positional Arguments:
  query_or_query_column         Single query to process or name of the CSV
                                column containing queries when using -i/--input.

Optional Arguments:
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
  --timezone TIMEZONE           Timezone for dates, for example 'Europe/Paris'.
                                Defaults to UTC.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the queries you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Searching user using "cancer" as a query:
    $ minet tw user-search cancer > users.csv

. Running multiple queries in series:
    $ minet tw user-search query -i queries.csv > users.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter user-search "value"

. Here is how to use a command with a CSV file:
    $ minet twitter user-search column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter user-search column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter user-search column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter user-search "value1,value2" --explode ","
```

### user-tweets

```
Usage: minet twitter user-tweets [-h] [--ids] [--silent]
                                 [--refresh-per-second REFRESH_PER_SECOND]
                                 [--simple-progress] [--min-date MIN_DATE]
                                 [--exclude-retweets] [--v2]
                                 [--timezone TIMEZONE] [--api-key API_KEY]
                                 [--rcfile RCFILE]
                                 [--api-secret-key API_SECRET_KEY]
                                 [--access-token ACCESS_TOKEN]
                                 [--access-token-secret ACCESS_TOKEN_SECRET]
                                 [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                 [--total TOTAL] [-o OUTPUT]
                                 user_or_user_column

# Minet Twitter User Tweets Command

Retrieve the last ~3200 tweets, including retweets from
the given Twitter users, using the API.

Positional Arguments:
  user_or_user_column           Single Twitter account screen name or id to
                                process or name of the CSV column containing
                                Twitter account screen names or ids when using
                                -i/--input.

Optional Arguments:
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
  --timezone TIMEZONE           Timezone for dates, for example 'Europe/Paris'.
                                Defaults to UTC.
  --v2                          Whether to use latest Twitter API v2 rather than
                                v1.1.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the Twitter account screen names or ids you want
                                to process. Will consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Getting tweets from users in a CSV file:
    $ minet tw user-tweets screen_name -i users.csv > tweets.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet twitter user-tweets "value"

. Here is how to use a command with a CSV file:
    $ minet twitter user-tweets column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet twitter user-tweets column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter user-tweets column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter user-tweets "value1,value2" --explode ","
```

## Wikipedia

### pageviews

```
Usage: minet wikipedia pageviews [-h] --start-date START_DATE [--silent]
                                 [--refresh-per-second REFRESH_PER_SECOND]
                                 [--simple-progress] --end-date END_DATE
                                 [--agent AGENT] [--access ACCESS] [-t THREADS]
                                 [--granularity GRANULARITY] [--sum]
                                 [--lang LANG] [--lang-column LANG_COLUMN]
                                 [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                 [--total TOTAL] [--resume] [-o OUTPUT]
                                 page_or_page_column

# Minet Wikipedia Pageviews Command

Command using the Wikimedia REST API to collect
pageviews for a given amount of Wikipedia pages.

See API documentation here for more details:
https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews

Positional Arguments:
  page_or_page_column           Single page to process or name of the CSV column
                                containing pages when using -i/--input.

Optional Arguments:
  --access ACCESS               Get pageviews by access. Defaults to
                                `all-access`.
  --agent AGENT                 Get pageviews by target agent. Defaults to
                                `all-agents`.
  --end-date END_DATE           End date. Must be of format YYYYMMDD (e.g.
                                20151031) or YYYYMMDDHH (e.g. 2015103100)
  --granularity GRANULARITY     Pageviews granularity. Defaults to `monthly`.
  --lang LANG                   Lang for the given pages.
  --lang-column LANG_COLUMN     Name of a CSV column containing page lang.
  --start-date START_DATE       Starting date. Must be of format YYYYMMDD (e.g.
                                20151031) or YYYYMMDDHH (e.g. 2015103100)
  --sum                         Whether to sum the collected pageviews rather
                                than outputting them by timestamp.
  -t, --threads THREADS         Number of threads to use. Defaults to `10`.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the pages you want to process. Will consider `-`
                                as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      Whether to resume from an aborted collection.
                                Need -o to be set. Will only work with --sum.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet wikipedia pageviews "value"

. Here is how to use a command with a CSV file:
    $ minet wikipedia pageviews column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet wikipedia pageviews column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet wikipedia pageviews column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet wikipedia pageviews "value1,value2" --explode ","
```

## Youtube

### captions

```
Usage: minet youtube captions [-h] [--lang LANG] [--silent]
                              [--refresh-per-second REFRESH_PER_SECOND]
                              [--simple-progress] [-c] [-i INPUT]
                              [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                              [-o OUTPUT]
                              video_or_video_column

# YouTube captions

Retrieve captions for the given YouTube videos.

Positional Arguments:
  video_or_video_column         Single video url or id to process or name of the
                                CSV column containing video urls or ids when
                                using -i/--input.

Optional Arguments:
  -c, --collapse                Use this flag to only emit one line per video,
                                with the subtitle lines joined together in a
                                single cell. Note that this means losing start &
                                duration information of the subtitles.
  --lang LANG                   Language (ISO code like "en") of captions to
                                retrieve. You can specify several languages by
                                preferred order separated by commas. Defaults to
                                `en`.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the video urls or ids you want to process. Will
                                consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching captions for a list of videos:
    $ minet yt captions video_id -i videos.csv > captions.csv

. Fetching French captions with a fallback to English:
    $ minet yt captions video_id -i videos.csv --lang fr,en > captions.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet youtube captions "value"

. Here is how to use a command with a CSV file:
    $ minet youtube captions column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet youtube captions column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube captions column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube captions "value1,value2" --explode ","
```

### channel-videos

```
Usage: minet youtube channel-videos [-h] [--start-time START_TIME] [--silent]
                                    [--refresh-per-second REFRESH_PER_SECOND]
                                    [--simple-progress] [--end-time END_TIME]
                                    [-k KEY] [--rcfile RCFILE] [-i INPUT]
                                    [--explode EXPLODE] [-s SELECT]
                                    [--total TOTAL] [-o OUTPUT]
                                    channel_or_channel_column

# YouTube channel videos

Retrieve metadata about all YouTube videos from one or many channel(s) using the API.

Under the hood, this command extract the channel id from the given url or scrape the
website to find it if necessary. Then the command uses the API to retrieve
information about videos stored in the main playlist of the channel
supposed to contain all the channel's videos.

Positional Arguments:
  channel_or_channel_column     Single channel to process or name of the CSV
                                column containing channels when using
                                -i/--input.

Optional Arguments:
  --end-time END_TIME           The newest UTC datetime from which the videos
                                will be retrieved (end-time is excluded).
                                Warning: videos more recent than end-time will
                                still be retrieved from the API, but they will
                                not be written in the output file. The date
                                should have the format: "YYYY-MM-DDTHH:mm:ssZ"
                                but incomplete dates will be completed for you
                                e.g. "2002-04".
  -k, --key KEY                 YouTube API Data dashboard API key. Can be used
                                more than once. Can also be configured in a
                                .minetrc file as "youtube.key" or read from the
                                MINET_YOUTUBE_KEY env variable.
  --start-time START_TIME       The oldest UTC datetime from which the videos
                                will be retrieved (start-time is included). The
                                date should have the format:
                                "YYYY-MM-DDTHH:mm:ssZ" but incomplete dates will
                                be completed for you e.g. "2002-04".
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the channels you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching all the videos from a channel based on the channel's id or url:
    $ minet youtube channel-videos https://www.youtube.com/c/LinksOff -k my-api-key > linksoff_videos.csv
    $ minet youtube channel-videos https://www.youtube.com/channel/UCqnbDFdCpuN8CMEg0VuEBqA -k my-api-key > thenewyorktimes_videos.csv
    $ minet youtube channel-videos UCprclkVrNPls7PR-nHhf1Ow -k my-api-key > tonyheller_videos.csv

. Fetching multiple channels' videos:
    $ minet youtube channel-videos channel_id -i channels_id.csv -k my-api-key > channels_videos.csv
    $ minet youtube channel-videos channel_url -i channels_url.csv -k my-api-key > channels_videos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet youtube channel-videos "value"

. Here is how to use a command with a CSV file:
    $ minet youtube channel-videos column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet youtube channel-videos column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube channel-videos column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube channel-videos "value1,value2" --explode ","
```

### channels

```
Usage: minet youtube channels [-h] [-k KEY] [--rcfile RCFILE] [--silent]
                              [--refresh-per-second REFRESH_PER_SECOND]
                              [--simple-progress] [-i INPUT] [--explode EXPLODE]
                              [-s SELECT] [--total TOTAL] [-o OUTPUT]
                              channel_or_channel_column

# YouTube Channels Command

Retrieve metadata about YouTube channel from one or many name(s) using the API.

Under the hood, this command extract the channel id from the given url or scrape the
website to find it if necessary. Then the command uses the API to retrieve
information about the channel.

Positional Arguments:
  channel_or_channel_column     Single channel to process or name of the CSV
                                column containing channels when using
                                -i/--input.

Optional Arguments:
  -k, --key KEY                 YouTube API Data dashboard API key. Can be used
                                more than once. Can also be configured in a
                                .minetrc file as "youtube.key" or read from the
                                MINET_YOUTUBE_KEY env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the channels you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching metadata from a channel based on the channel's id or url:
    $ minet youtube channels https://www.youtube.com/c/LinksOff -k my-api-key > linksoff_meta.csv
    $ minet youtube channels https://www.youtube.com/channel/UCqnbDFdCpuN8CMEg0VuEBqA -k my-api-key > thenewyorktimes_meta.csv
    $ minet youtube channels UCprclkVrNPls7PR-nHhf1Ow -k my-api-key > tonyheller_meta.csv

. Fetching multiple channels' metadata:
    $ minet youtube channels channel_id -i channels_id.csv -k my-api-key > channels.csv
    $ minet youtube channels channel_url -i channels_url.csv -k my-api-key > channels.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet youtube channels "value"

. Here is how to use a command with a CSV file:
    $ minet youtube channels column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet youtube channels column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube channels column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube channels "value1,value2" --explode ","
```

### comments

```
Usage: minet youtube comments [-h] [-k KEY] [--rcfile RCFILE] [--silent]
                              [--refresh-per-second REFRESH_PER_SECOND]
                              [--simple-progress] [-i INPUT] [--explode EXPLODE]
                              [-s SELECT] [--total TOTAL] [-o OUTPUT]
                              video_or_video_column

# YouTube comments

Retrieve metadata about YouTube comments using the API.

Positional Arguments:
  video_or_video_column         Single video to process or name of the CSV
                                column containing videos when using -i/--input.

Optional Arguments:
  -k, --key KEY                 YouTube API Data dashboard API key. Can be used
                                more than once. Can also be configured in a
                                .minetrc file as "youtube.key" or read from the
                                MINET_YOUTUBE_KEY env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the videos you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching a video's comments:
    $ minet yt comments https://www.youtube.com/watch?v=7JTb2vf1OQQ -k my-api-key > comments.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet youtube comments "value"

. Here is how to use a command with a CSV file:
    $ minet youtube comments column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet youtube comments column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube comments column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube comments "value1,value2" --explode ","
```

### search

```
Usage: minet youtube search [-h] [-l LIMIT] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [--simple-progress]
                            [--order {date,rating,relevance,title,videoCount,viewCount}]
                            [-k KEY] [--rcfile RCFILE] [-i INPUT]
                            [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                            [-o OUTPUT]
                            query_or_query_column

# YouTube search

Search videos using the YouTube API.

Note that, even if undocumented, the API will never return
more than approx. 500 videos for a given query.

Positional Arguments:
  query_or_query_column         Single query to process or name of the CSV
                                column containing queries when using -i/--input.

Optional Arguments:
  -k, --key KEY                 YouTube API Data dashboard API key. Can be used
                                more than once. Can also be configured in a
                                .minetrc file as "youtube.key" or read from the
                                MINET_YOUTUBE_KEY env variable.
  -l, --limit LIMIT             Maximum number of videos to retrieve per query.
  --order {date,rating,relevance,title,videoCount,viewCount}
                                Order in which videos are retrieved. The default
                                one is relevance. Defaults to `relevance`.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the queries you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Searching videos about birds:
    $ minet youtube search bird -k my-api-key > bird_videos.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet youtube search "value"

. Here is how to use a command with a CSV file:
    $ minet youtube search column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet youtube search column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube search column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube search "value1,value2" --explode ","
```

### videos

```
Usage: minet youtube videos [-h] [-k KEY] [--rcfile RCFILE] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [--simple-progress] [-i INPUT] [--explode EXPLODE]
                            [-s SELECT] [--total TOTAL] [-o OUTPUT]
                            video_or_video_column

# YouTube videos

Retrieve metadata about YouTube videos using the API.

Positional Arguments:
  video_or_video_column         Single video to process or name of the CSV
                                column containing videos when using -i/--input.

Optional Arguments:
  -k, --key KEY                 YouTube API Data dashboard API key. Can be used
                                more than once. Can also be configured in a
                                .minetrc file as "youtube.key" or read from the
                                MINET_YOUTUBE_KEY env variable.
  -s, --select SELECT           Columns of -i/--input CSV file to include in the
                                output (separated by `,`). Use an empty string
                                if you don't want to keep anything: --select ''.
  --explode EXPLODE             Use to indicate the character used to separate
                                multiple values in a single CSV cell. Defaults
                                to none, i.e. CSV cells having a single values,
                                which is usually the case.
  --total TOTAL                 Total number of items to process. Might be
                                necessary when you want to display a finite
                                progress indicator for large files given as
                                input to the command.
  -i, --input INPUT             CSV file (potentially gzipped) containing all
                                the videos you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --rcfile RCFILE               Custom path to a minet configuration file. More
                                info about this here:
                                https://github.com/medialab/minet/blob/master/do
                                cs/cli.md#minetrc
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --simple-progress             Whether to simplify the progress bar and make it
                                fit on a single line. Can be useful in terminals
                                with partial ANSI support, e.g. a Jupyter
                                notebook cell.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet youtube videos "value"

. Here is how to use a command with a CSV file:
    $ minet youtube videos column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xan search -s col . | minet youtube videos column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube videos column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube videos "value1,value2" --explode ","
```

