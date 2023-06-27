# Minet Command Line Usage

## Summary

_Global utilities_

- [-h/--help/help](#help-flag)
- [--version](#version-flag)
- [minetrc config files](#minetrc)
- [minet environment variables](#envvars)

_Generic commands_

- [cookies](#cookies)
- [crawl](#crawl)
- [focus-crawl](#focus-crawl)
- [fetch](#fetch)
- [extract](#extract)
- [resolve](#resolve)
- [scrape](#scrape)
- [url-extract](#url-extract)
- [url-join](#url-join)
- [url-parse](#url-parse)

_Platform-related commands_

- [buzzsumo (bz)](#buzzsumo)
  - [limit](#buzzsumo-limit)
  - [domain-summary](#buzzsumo-domain-summary)
  - [domain](#buzzsumo-domain)
- [crowdtangle (ct)](#crowdtangle)
  - [leaderboard](#leaderboard)
  - [lists](#lists)
  - [posts-by-id](#posts-by-id)
  - [posts](#posts)
  - [search](#ct-search)
  - [summary](#summary)
- [facebook (fb)](#facebook)
  - [comments](#facebook-comments)
  - [post](#facebook-post)
  - [posts](#facebook-posts)
  - [post-authors](#facebook-post-authors)
  - [url-likes](#facebook-url-likes)
- [google](#google)
  - [sheets](#google-sheets)
- [hyphe](#hyphe)
  - [declare](#hyphe-declare)
  - [destroy](#hyphe-destroy)
  - [dump](#hyphe-dump)
  - [reset](#hyphe-reset)
  - [tag](#hyphe-tag)
- [instagram (insta)](#instagram)
  - [comments](#insta-comments)
  - [hashtag](#hashtag)
  - [post-infos](#insta-post-infos)
  - [user-followers](#user-followers)
  - [user-following](#user-following)
  - [user-infos](#user-infos)
  - [user-posts](#user-posts)
- [mediacloud (mc)](#mediacloud)
  - [medias](#mc-medias)
  - [search](#mc-search)
  - [topic](#topic)
    - [stories](#stories)
- [telegram (tl)](#telegram)
  - [channel-infos](#channel-infos)
  - [channel-messages](#channel-messages)
- [tiktok (tk)](#tiktok)
  - [search-videos](#search-videos)
- [twitter](#twitter)
  - [attrition](#attrition)
  - [followers](#followers)
  - [friends](#friends)
  - [list-followers](#list-followers)
  - [list-members](#list-members)
  - [retweeters](#retweeters)
  - [scrape](#twitter-scrape)
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
  - [comments](#youtube-comments)
  - [search](#youtube-search)
  - [videos](#videos)

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

- `./.minetrc{,.yml,.yaml,.json}`
- `~/.minetrc{,.yml,.yaml,.json}`

_Configuration file_

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
  cookie: "MY_TWITTER_COOKIE" # Used as --cookie for `minet tw scrape` command
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
Usage: minet cookies [-h] [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                     [--csv] [--url URL] [-o OUTPUT]
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
Usage: minet crawl [-h] [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                   [-O OUTPUT_DIR] [--resume] [-m MAX_DEPTH]
                   [--throttle THROTTLE] [-t THREADS] [--compress] [-w] [-d]
                   [--folder-strategy FOLDER_STRATEGY] [-f {csv,jsonl,ndjson}]
                   [-v] [-n] [-u] [-i INPUT] [--explode EXPLODE] [-s SELECT]
                   [--total TOTAL]
                   target [url_or_url_column]

# Minet Crawl Command

Run a crawl using a minet crawler or spiders defined
in a python module.

Positional Arguments:
  target                        Crawling target.
  url_or_url_column             Single start url to process or name of the CSV
                                column containing start urls when using
                                -i/--input. Defaults to "url".

Optional Arguments:
  --compress                    Whether to compress the downloaded files when
                                saving on disk using -w/--write.
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
  -m, --max-depth MAX_DEPTH     Maximum depth for the crawl.
  -n, --normalized-url-cache    Whether to normalize url cache when using
                                -u/--visit-urls-only-once.
  -O, --output-dir OUTPUT_DIR   Output directory. Defaults to `crawl`.
  -t, --threads THREADS         Number of threads to use. You can use `0` if you
                                want the crawler to remain completely
                                synchronous. Defaults to `25`.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to `0.2`.
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
    "www.", or "m." or "fr.", for instance).

Examples:

. Crawling using the `process` function in the `crawl` module:
    $ minet crawl crawl:process -O crawl-data
```

## focus-crawl

```
Usage: minet focus-crawl [-h] [-C CONTENT_FILTER] [--silent]
                         [--refresh-per-second REFRESH_PER_SECOND]
                         [-U URL_FILTER] [--extract] [--irrelevant-continue]
                         [--only-html] [-O OUTPUT_DIR] [--resume] [-m MAX_DEPTH]
                         [--throttle THROTTLE] [-t THREADS] [--compress] [-w]
                         [-d] [--folder-strategy FOLDER_STRATEGY]
                         [-f {csv,jsonl,ndjson}] [-v] [-n] [-i INPUT]
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
  --compress                    Whether to compress the downloaded files when
                                saving on disk using -w/--write.
  -C, --content-filter CONTENT_FILTER
                                Regex used to filter fetched content.
  --extract                     Perform regex match on extracted text content
                                instead of html content using the Trafilatura
                                library.
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
  --irrelevant-continue         Continue exploration whether met content is
                                relevant or not.
  -m, --max-depth MAX_DEPTH     Maximum depth for the crawl.
  -n, --normalized-url-cache    Whether to normalize url cache when using
                                -u/--visit-urls-only-once.
  --only-html                   Add URLs to the crawler queue only if they seem
                                to lead to a HTML content.
  -O, --output-dir OUTPUT_DIR   Output directory. Defaults to `crawl`.
  -t, --threads THREADS         Number of threads to use. You can use `0` if you
                                want the crawler to remain completely
                                synchronous. Defaults to `25`.
  --throttle THROTTLE           Time to wait - in seconds - between 2 calls to
                                the same domain. Defaults to `0.2`.
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
    "www.", or "m." or "fr.", for instance).

Examples:

. Running a simple crawler:
    $ minet focus-crawl url -i urls.csv --content-filter '(?:assembl[ée]e nationale|s[ée]nat)' -O ./result
```

## fetch

```
Usage: minet fetch [-h] [--domain-parallelism DOMAIN_PARALLELISM] [--silent]
                   [--refresh-per-second REFRESH_PER_SECOND]
                   [-g {brave,chrome,chromium,edge,firefox,opera,opera_gx,safari,vivaldi}]
                   [-H HEADERS] [--insecure] [-t THREADS] [--throttle THROTTLE]
                   [--timeout TIMEOUT] [--url-template URL_TEMPLATE] [-X METHOD]
                   [--max-redirects MAX_REDIRECTS] [--compress] [-c] [-D]
                   [-O OUTPUT_DIR] [-f FILENAME]
                   [--filename-template FILENAME_TEMPLATE]
                   [--folder-strategy FOLDER_STRATEGY] [--keep-failed-contents]
                   [--standardize-encoding] [--only-html] [-i INPUT]
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
  --compress                    Whether to compress the contents.
  -c, --contents-in-report, -w, --no-contents-in-report
                                Whether to include retrieved contents, e.g.
                                html, directly in the report and avoid writing
                                them in a separate folder. This requires to
                                standardize encoding and won't work on binary
                                formats. Note that --contents-in-report is the
                                default when no input file is given.
  --domain-parallelism DOMAIN_PARALLELISM
                                Max number of urls per domain to hit at the same
                                time. Defaults to `1`.
  -f, --filename FILENAME       Name of the column used to build retrieved file
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
  --insecure                    Whether to allow ssl errors when performing
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
  -X, --request METHOD          The http method to use. Will default to GET.
                                Defaults to `GET`.
  -D, --dont-save               Use not to write any downloaded file on disk.
  --standardize-encoding        Whether to systematically convert retrieved text
                                to UTF-8.
  -t, --threads THREADS         Number of threads to use. Defaults to `25`.
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
  --resume                      "Whether to resume from an aborted collection.
                                Need -o to be set.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Columns being added to the output:

. "fetch_original_index": index of the line in the original file (the output will be
    arbitrarily ordered since multiple requests are performed concurrently).
. "resolved_url": final resolved url (after templating & solving redirects).
. "http_status": HTTP status code of the request, e.g. 200, 404, 503 etc.
. "datetime_utc": datetime when the response was finished.
. "fetch_error": an error code if anything went wrong when performing the request.
. "filename": path to the downloaded file, relative to the folder given
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
    "www.", or "m." or "fr.", for instance).

Examples:

. Fetching a single url (can be useful when piping):
    $ minet fetch "https://www.lemonde.fr"

. Fetching a batch of url from existing CSV file:
    $ minet fetch url -i file.csv > report.csv

. CSV input from stdin (mind the `-`):
    $ xsv select url file.csv | minet fetch url -i - > report.csv

. Dowloading files in specific output directory:
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
    $ xsv search -s col . | minet fetch column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet fetch column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet fetch "value1,value2" --explode ","
```

## extract

```
Usage: minet extract [-h] [-g] [--silent]
                     [--refresh-per-second REFRESH_PER_SECOND] [-I INPUT_DIR]
                     [-p PROCESSES] [--chunk-size CHUNK_SIZE]
                     [--body-column BODY_COLUMN] [--error-column ERROR_COLUMN]
                     [--status-column STATUS_COLUMN]
                     [--encoding-column ENCODING_COLUMN]
                     [--mimetype-column MIMETYPE_COLUMN] [--encoding ENCODING]
                     [-i INPUT] [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                     [--resume] [-o OUTPUT]
                     [filename_or_filename_column]

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
containing columns like "filename", "http_status", "encoding" etc. as
you can find in a fetch command CSV report.

This said, you can of course feed this command any kind of CSV data,
and use dedicated flags such as --status-column, --body-column to
to inform the command about your specific table.

The comand is also able to work on glob patterns, such as: "downloaded/**/*.html",
and can also be fed CSV columns containing HTML content directly if
required.

Positional Arguments:
  filename_or_filename_column   Single filename to process or name of the CSV
                                column containing filenames when using
                                -i/--input. Defaults to "filename".

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
  -g, --glob                    Will interpret given filename as glob patterns
                                to resolve if given.
  -I, --input-dir INPUT_DIR     Directory where the HTML files are stored.
  --mimetype-column MIMETYPE_COLUMN
                                Name of the CSV column containing file mimetype.
                                Defaults to `mimetype`.
  -p, --processes PROCESSES     Number of processes to use. Defaults to roughly
                                half of the available CPUs.
  --status-column STATUS_COLUMN
                                Name of the CSV column containing HTTP status.
                                Defaults to `http_status`.
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
                                the filenames you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      "Whether to resume from an aborted collection.
                                Need -o to be set.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
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

Examples:

. Extracting content from a single file on disk:
    $ minet extract ./path/to/file.html

. Extracting content from a `minet fetch` report:
    $ minet extract -i report.csv -I downloaded > extracted.csv

. Extracting content from a single url:
    $ minet fetch "https://lemonde.fr" | minet extract -i -

. Indicating a custom filename column (named "path"):
    $ minet extract path -i report.csv -I downloaded > extracted.csv

. Extracting content from a CSV colum containing HTML directly:
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
                     [-g {brave,chrome,chromium,edge,firefox,opera,opera_gx,safari,vivaldi}]
                     [-H HEADERS] [--insecure] [-t THREADS]
                     [--throttle THROTTLE] [--timeout TIMEOUT]
                     [--url-template URL_TEMPLATE] [-X METHOD]
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
  --insecure                    Whether to allow ssl errors when performing
                                requests or not.
  --max-redirects MAX_REDIRECTS
                                Maximum number of redirections to follow before
                                breaking. Defaults to `20`.
  --only-shortened              Whether to only attempt to resolve urls that are
                                probably shortened.
  -X, --request METHOD          The http method to use. Will default to GET.
                                Defaults to `GET`.
  -t, --threads THREADS         Number of threads to use. Defaults to `25`.
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
  --resume                      "Whether to resume from an aborted collection.
                                Need -o to be set.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
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
    $ minet resolve url_column file.csv > report.csv

. CSV input from stdin (mind the `-`):
    $ xsv select url_column file.csv | minet resolve url_column - > report.csv

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
    $ xsv search -s col . | minet fetch column_name -i -

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
                    [-g] [-I INPUT_DIR] [-p PROCESSES] [--chunk-size CHUNK_SIZE]
                    [--body-column BODY_COLUMN] [--url-column URL_COLUMN]
                    [--error-column ERROR_COLUMN]
                    [--status-column STATUS_COLUMN]
                    [--encoding-column ENCODING_COLUMN]
                    [--mimetype-column MIMETYPE_COLUMN] [--encoding ENCODING]
                    [-f {csv,jsonl,ndjson}]
                    [--plural-separator PLURAL_SEPARATOR] [--strain STRAIN]
                    [-i INPUT] [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                    [-o OUTPUT]
                    scraper [filename_or_filename_column]

# Minet Scrape Command

Use multiple processes to scrape data from a batch of HTML files using
minet scraping DSL documented here:
https://github.com/medialab/minet/blob/master/docs/cookbook/scraping_dsl.md

It will output the scraped items as a CSV or NDJSON file.

Note that this command has been geared towards working in tandem with
the fetch command. This means the command expects, by default, CSV files
containing columns like "filename", "http_status", "encoding" etc. as
you can find in a fetch command CSV report.

This said, you can of course feed this command any kind of CSV data,
and use dedicated flags such as --status-column, --body-column to
to inform the command about your specific table.

The comand is also able to work on glob patterns, such as: "downloaded/**/*.html",
and can also be fed CSV columns containing HTML content directly if
required.

Positional Arguments:
  scraper                       Path to a scraper definition file, or name of a
                                builtin scraper, e.g. "title". See the complete
                                list below.
  filename_or_filename_column   Single filename to process or name of the CSV
                                column containing filenames when using
                                -i/--input. Defaults to "filename".

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
  -f, --format {csv,jsonl,ndjson}
                                Output format. Defaults to `csv`.
  -g, --glob                    Will interpret given filename as glob patterns
                                to resolve if given.
  -I, --input-dir INPUT_DIR     Directory where the HTML files are stored.
  --mimetype-column MIMETYPE_COLUMN
                                Name of the CSV column containing file mimetype.
                                Defaults to `mimetype`.
  --plural-separator PLURAL_SEPARATOR
                                Separator use to join lists of values when
                                serializing to CSV. Defaults to `|`.
  -p, --processes PROCESSES     Number of processes to use. Defaults to roughly
                                half of the available CPUs.
  --status-column STATUS_COLUMN
                                Name of the CSV column containing HTTP status.
                                Defaults to `http_status`.
  --strain STRAIN               Optional CSS selector used to strain, i.e. only
                                parse matched tags in the parsed html files in
                                order to optimize performance.
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
                                the filenames you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Builtin scrapers:

. "canonical": scrape the <link rel="canonical"> tag href if any.
. "title": scrape the <title> tag if any.
. "urls": scrape all the relevant <a> tag href urls. Will join them
    with the correct base url if --url-column was given.

Examples:

. Scraping a single file on disk:
    $ minet scrape scraper.yml ./path/to/file.html

. Scraping a `minet fetch` report:
    $ minet scrape scraper.yml -i report.csv -I downloaded > scraped.csv

. Scraping a single url:
    $ minet fetch "https://lemonde.fr" | minet scrape scraper.yml -i -

. Indicating a custom filename column (named "path"):
    $ minet scrape scraper.yml path -i report.csv -I downloaded > scraped.csv

. Scraping a CSV colum containing HTML directly:
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

. Keeping some columns from input CSV file:
    $ minet scrape scraper.yml -i report.csv -s name,url > scraped.csv

. Using a builtin scraper:
    $ minet scrape title -i report.csv > titles.csv
```

## url-extract

```
Usage: minet url-extract [-h] [--silent]
                         [--refresh-per-second REFRESH_PER_SECOND]
                         [--base-url BASE_URL] [--from {html,text}] [-s SELECT]
                         [--total TOTAL] [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Extracting urls from a text column:
    $ minet url-extract text posts.csv > urls.csv

. Extracting urls from a html column:
    $ minet url-extract html --from html posts.csv > urls.csv
```

## url-join

```
Usage: minet url-join [-h] [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                      [-p MATCH_COLUMN_PREFIX] [--separator SEPARATOR]
                      [-s SELECT] [-o OUTPUT]
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
    $ xsv select url webentities.csv | minet url-join url - post_url posts.csv > joined.csv
```

## url-parse

```
Usage: minet url-parse [-h] [--facebook] [--silent]
                       [--refresh-per-second REFRESH_PER_SECOND] [--twitter]
                       [--youtube] [--infer-redirection] [--fix-common-mistakes]
                       [--normalize-amp] [--quoted] [--sort-query]
                       [--strip-authentication] [--strip-fragment]
                       [--strip-index] [--strip-irrelevant-subdomains]
                       [--strip-lang-query-items] [--strip-lang-subdomains]
                       [--strip-protocol] [--strip-trailing-slash] [-i INPUT]
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
  --quoted, --no-quoted         Whether or not to normalize to a quoted or
                                unquoted version of the url when normalizing
                                url. Defaults to `True`.
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
  --strip-lang-query-items, --dont-strip-lang-query-items
                                Whether or not to strip language query items
                                (ex: `gl=pt_BR`) when normalizing url. Defaults
                                to `False`.
  --strip-lang-subdomains, --dont-strip-lang-subdomains
                                Whether or not to strip language subdomains (ex:
                                `fr-FR.lemonde.fr` to only `lemonde.fr` because
                                `fr-FR` isn't a relevant subdomain, it indicates
                                the language and the country) when normalizing
                                url. Defaults to `False`.
  --strip-protocol, --dont-strip-protocol
                                Whether or not to strip the protocol when
                                normalizing the url. Defaults to `True`.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Columns being added to the output:

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
    $ xsv search -s col . | minet url-parse column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet url-parse column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet url-parse "value1,value2" --explode ","
```

## BuzzSumo

```
Usage: minet buzzsumo [-h] [-t TOKEN] [--rcfile RCFILE] [--silent]
                      [--refresh-per-second REFRESH_PER_SECOND]
                      {limit,domain,domain-summary} ...

# Minet Buzzsumo Command

Gather data from the BuzzSumo APIs easily and efficiently.

Optional Arguments:
  -t, --token TOKEN             BuzzSumo API token. Can also be configured in a
                                .minetrc file as "buzzsumo.token" or read from
                                the MINET_BUZZSUMO_TOKEN env variable.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Subcommands:
  {limit,domain,domain-summary}
                                Subcommand to use.
```

<h3 id="buzzsumo-limit">limit</h3>

```
Usage: minet buzzsumo limit [-h] [-t TOKEN] [--rcfile RCFILE] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [-o OUTPUT]

# Minet Buzzsumo Limit Command

Call BuzzSumo for a given request and return the remaining number
of calls for this month contained in the request's headers.

Optional Arguments:
  -t, --token TOKEN             BuzzSumo API token. Can also be configured in a
                                .minetrc file as "buzzsumo.token" or read from
                                the MINET_BUZZSUMO_TOKEN env variable.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Returning the remaining number of calls for this month:
    $ minet bz limit --token YOUR_TOKEN
```

<h3 id="buzzsumo-domain-summary">domain-summary</h3>

```
Usage: minet buzzsumo domain-summary [-h] [-t TOKEN] [--rcfile RCFILE]
                                     [--silent]
                                     [--refresh-per-second REFRESH_PER_SECOND]
                                     --begin-date BEGIN_DATE --end-date END_DATE
                                     [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                     [--total TOTAL] [-o OUTPUT]
                                     domain_name_or_domain_name_column

# Minet Buzzsumo Domain Summary Command

Gather information about the quantity of articles crawled by BuzzSumo for certain domain names and a given period.

Inform the user about the number of calls (corresponding to the number of pages) needed to request BuzzSumo about those domain names.

Positional Arguments:
  domain_name_or_domain_name_column
                                Single domain name to process or name of the CSV
                                column containing domain names when using
                                -i/--input.

Optional Arguments:
  --begin-date BEGIN_DATE       The date you wish to fetch articles from. UTC
                                date should have the following format :
                                YYYY-MM-DD
  --end-date END_DATE           The date you wish to fetch articles to. UTC date
                                should have the following format : YYYY-MM-DD
  -t, --token TOKEN             BuzzSumo API token. Can also be configured in a
                                .minetrc file as "buzzsumo.token" or read from
                                the MINET_BUZZSUMO_TOKEN env variable.
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
                                the domain names you want to process. Will
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Returning the number of articles and pages found in BuzzSumo for one domain name:
    $ minet bz domain-summary 'nytimes.com' --begin-date 2019-01-01 --end-date 2019-03-01 --token YOUR_TOKEN

. Returning the number of articles and pages found in BuzzSumo for a list of domain names in a CSV:
    $ minet bz domain-summary domain_name domain_names.csv --begin-date 2020-01-01 --end-date 2021-06-15 --token YOUR_TOKEN  > domain_name_summary.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet buzzsumo domain-summary "value"

. Here is how to use a command with a CSV file:
    $ minet buzzsumo domain-summary column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet buzzsumo domain-summary column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet buzzsumo domain-summary column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet buzzsumo domain-summary "value1,value2" --explode ","
```

<h3 id="buzzsumo-domain">domain</h3>

```
Usage: minet buzzsumo domain [-h] [-t TOKEN] [--rcfile RCFILE] [--silent]
                             [--refresh-per-second REFRESH_PER_SECOND]
                             --begin-date BEGIN_DATE --end-date END_DATE
                             [-i INPUT] [--explode EXPLODE] [-s SELECT]
                             [--total TOTAL] [-o OUTPUT]
                             domain_name_or_domain_name_column

# Minet Buzzsumo Domain Command

Gather social media information about all the articles crawled by BuzzSumo for one or a list of domain names and over a given period.

The link to the official documentation: https://developers.buzzsumo.com/reference/articles.

Positional Arguments:
  domain_name_or_domain_name_column
                                Single domain name to process or name of the CSV
                                column containing domain names when using
                                -i/--input.

Optional Arguments:
  --begin-date BEGIN_DATE       The date you wish to fetch articles from. UTC
                                date should have the following format :
                                YYYY-MM-DD
  --end-date END_DATE           The date you wish to fetch articles to. UTC date
                                should have the following format : YYYY-MM-DD
  -t, --token TOKEN             BuzzSumo API token. Can also be configured in a
                                .minetrc file as "buzzsumo.token" or read from
                                the MINET_BUZZSUMO_TOKEN env variable.
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
                                the domain names you want to process. Will
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Returning social media information for one domain name:
    $ minet bz domain 'trump-feed.com' --begin-date 2021-01-01 --end-date 2021-06-30 --token YOUR_TOKEN > trump_feed_articles.csv

. Returning social media information for a list of domain names in a CSV:
    $ minet bz domain domain_name domain_names.csv --select domain_name --begin-date 2019-01-01 --end-date 2020-12-31 --token YOUR_TOKEN > domain_name_articles.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet buzzsumo domain "value"

. Here is how to use a command with a CSV file:
    $ minet buzzsumo domain column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet buzzsumo domain column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet buzzsumo domain column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet buzzsumo domain "value1,value2" --explode ","
```

## CrowdTangle

```
Usage: minet crowdtangle [-h] [--rate-limit RATE_LIMIT] [--rcfile RCFILE]
                         [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                         [-t TOKEN]
                         {leaderboard,lists,posts-by-id,posts,search,summary}
                         ...

# Minet Crowdtangle Command

Gather data from the CrowdTangle APIs easily and efficiently.

Optional Arguments:
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to `6`. Can also be configured in a .minetrc
                                file as "crowdtangle.rate_limit" or read from
                                the MINET_CROWDTANGLE_RATE_LIMIT env variable.
  -t, --token TOKEN             CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Subcommands:
  {leaderboard,lists,posts-by-id,posts,search,summary}
                                Subcommand to use.
```

### leaderboard

```
Usage: minet crowdtangle leaderboard [-h] [--rate-limit RATE_LIMIT]
                                     [--rcfile RCFILE] [--silent]
                                     [--refresh-per-second REFRESH_PER_SECOND]
                                     [-t TOKEN] [--breakdown] [-f {csv,jsonl}]
                                     [-l LIMIT] [--list-id LIST_ID]
                                     [--start-date START_DATE] [-o OUTPUT]

# Minet CrowdTangle Leaderboard Command

Gather information and aggregated stats about pages and groups of the designated dashboard (indicated by a given token).

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Leaderboard.

Optional Arguments:
  --breakdown, --no-breakdown   Whether to skip statistics breakdown by post
                                type in the CSV output. Defaults to `True`.
  -f, --format {csv,jsonl}      Output format. Defaults to `csv`.
  -l, --limit LIMIT             Maximum number of accounts to retrieve. Will
                                fetch every account by default.
  --list-id LIST_ID             Optional list id from which to retrieve
                                accounts.
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to `6`. Can also be configured in a .minetrc
                                file as "crowdtangle.rate_limit" or read from
                                the MINET_CROWDTANGLE_RATE_LIMIT env variable.
  --start-date START_DATE       The earliest date at which to start aggregating
                                statistics (UTC!). You can pass just a year or a
                                year-month for convenience.
  -t, --token TOKEN             CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching accounts statistics for every account in your dashboard:
    $ minet ct leaderboard --token YOUR_TOKEN > accounts-stats.csv
```

### lists

```
Usage: minet crowdtangle lists [-h] [--rate-limit RATE_LIMIT] [--rcfile RCFILE]
                               [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [-t TOKEN] [-o OUTPUT]

# Minet CrowdTangle Lists Command

Retrieve the lists from a CrowdTangle dashboard (indicated by a given token).

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Lists.

Optional Arguments:
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to `6`. Can also be configured in a .minetrc
                                file as "crowdtangle.rate_limit" or read from
                                the MINET_CROWDTANGLE_RATE_LIMIT env variable.
  -t, --token TOKEN             CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching a dashboard's lists:
    $ minet ct lists --token YOUR_TOKEN > lists.csv
```

### posts-by-id

```
Usage: minet crowdtangle posts-by-id [-h] [--rate-limit RATE_LIMIT]
                                     [--rcfile RCFILE] [--silent]
                                     [--refresh-per-second REFRESH_PER_SECOND]
                                     [-t TOKEN] [-i INPUT] [--explode EXPLODE]
                                     [-s SELECT] [--total TOTAL] [--resume]
                                     [-o OUTPUT]
                                     post_url_or_id_or_post_url_or_id_column

# Minet CrowdTangle Post By Id Command

Retrieve metadata about batches of posts using Crowdtangle's API.

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Posts#get-postid.

Positional Arguments:
  post_url_or_id_or_post_url_or_id_column
                                Single URL or id to process or name of the CSV
                                column containing URLs or ids when using
                                -i/--input.

Optional Arguments:
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to `6`. Can also be configured in a .minetrc
                                file as "crowdtangle.rate_limit" or read from
                                the MINET_CROWDTANGLE_RATE_LIMIT env variable.
  -t, --token TOKEN             CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
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
                                the URLs or ids you want to process. Will
                                consider `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      "Whether to resume from an aborted collection.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Retrieving information about a batch of posts:
    $ minet ct posts-by-id post-url posts.csv --token YOUR_TOKEN > metadata.csv

. Retrieving information about a single post:
    $ minet ct posts-by-id 1784333048289665 --token YOUR_TOKEN

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet crowdtangle posts-by-id "value"

. Here is how to use a command with a CSV file:
    $ minet crowdtangle posts-by-id column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet crowdtangle posts-by-id column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet crowdtangle posts-by-id column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet crowdtangle posts-by-id "value1,value2" --explode ","
```

### posts

```
Usage: minet crowdtangle posts [-h] [--rate-limit RATE_LIMIT] [--rcfile RCFILE]
                               [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [-t TOKEN] [--chunk-size CHUNK_SIZE]
                               [--end-date END_DATE] [-f {csv,jsonl}]
                               [--language LANGUAGE] [-l LIMIT]
                               [--list-ids LIST_IDS]
                               [--sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}]
                               [--start-date START_DATE] [--resume] [-o OUTPUT]

# Minet CrowdTangle Posts Command

Gather post data from the designated dashboard (indicated by a given token).

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Posts.

Optional Arguments:
  --chunk-size CHUNK_SIZE       When sorting by date (default), the number of
                                items to retrieve before shifting the inital
                                query to circumvent the APIs limitations.
                                Defaults to `500`.
  --end-date END_DATE           The latest date at which a post could be posted
                                (UTC!). You can pass just a year or a year-month
                                for convenience.
  -f, --format {csv,jsonl}      Output format. Defaults to `csv`.
  --language LANGUAGE           Language of posts to retrieve.
  -l, --limit LIMIT             Maximum number of posts to retrieve. Will fetch
                                every post by default.
  --list-ids LIST_IDS           Ids of the lists from which to retrieve posts,
                                separated by commas.
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to `6`. Can also be configured in a .minetrc
                                file as "crowdtangle.rate_limit" or read from
                                the MINET_CROWDTANGLE_RATE_LIMIT env variable.
  --sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}
                                The order in which to retrieve posts. Defaults
                                to `date`.
  --start-date START_DATE       The earliest date at which a post could be
                                posted (UTC!). You can pass just a year or a
                                year-month for convenience. Defaults to `2010`.
  -t, --token TOKEN             CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      "Whether to resume from an aborted collection.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

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
Usage: minet crowdtangle search [-h] [--rate-limit RATE_LIMIT] [--rcfile RCFILE]
                                [--silent]
                                [--refresh-per-second REFRESH_PER_SECOND]
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

# Minet CrowdTangle Search Command

Search posts on the whole CrowdTangle platform.

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Search.

Positional Arguments:
  terms                         The search query term or terms.

Optional Arguments:
  --and AND                     AND clause to add to the query terms.
  --chunk-size CHUNK_SIZE       When sorting by date (default), the number of
                                items to retrieve before shifting the inital
                                query to circumvent the APIs limitations.
                                Defaults to `500`.
  --end-date END_DATE           The latest date at which a post could be posted
                                (UTC!). You can pass just a year or a year-month
                                for convenience.
  -f, --format {csv,jsonl}      Output format. Defaults to `csv`.
  --in-list-ids IN_LIST_IDS     Ids of the lists in which to search, separated
                                by commas.
  --language LANGUAGE           Language ISO code like "fr" or "zh-CN".
  -l, --limit LIMIT             Maximum number of posts to retrieve. Will fetch
                                every post by default.
  --not-in-title                Whether to search terms in account titles also.
  --offset OFFSET               Count offset.
  -p, --platforms PLATFORMS     The platforms from which to retrieve links
                                (facebook, instagram, or reddit). This value can
                                be comma-separated.
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to `6`. Can also be configured in a .minetrc
                                file as "crowdtangle.rate_limit" or read from
                                the MINET_CROWDTANGLE_RATE_LIMIT env variable.
  --search-field {account_name_only,image_text_only,include_query_strings,text_fields_and_image_text,text_fields_only}
                                In what to search the query. Defaults to
                                `text_fields_and_image_text`.
  --sort-by {date,interaction_rate,overperforming,total_interactions,underperforming}
                                The order in which to retrieve posts. Defaults
                                to `date`.
  --start-date START_DATE       The earliest date at which a post could be
                                posted (UTC!). You can pass just a year or a
                                year-month for convenience. Defaults to `2010`.
  -t, --token TOKEN             CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
  --types TYPES                 Types of post to include, separated by comma.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching all the 2021 posts containing the words 'acetylsalicylic acid':
    $ minet ct search 'acetylsalicylic acid' --start-date 2021-01-01 --token YOUR_TOKEN > posts.csv
```

### summary

```
Usage: minet crowdtangle summary [-h] [--rate-limit RATE_LIMIT]
                                 [--rcfile RCFILE] [--silent]
                                 [--refresh-per-second REFRESH_PER_SECOND]
                                 [-t TOKEN] [-p PLATFORMS] [--posts POSTS]
                                 [--sort-by {date,subscriber_count,total_interactions}]
                                 --start-date START_DATE [-i INPUT]
                                 [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                                 [-o OUTPUT]
                                 url_or_url_column

# Minet CrowdTangle Link Summary Command

Retrieve aggregated statistics about link sharing on the Crowdtangle API and by platform.

For more information, see the API endpoint documentation: https://github.com/CrowdTangle/API/wiki/Links.

Positional Arguments:
  url_or_url_column             Single URL to process or name of the CSV column
                                containing URLs when using -i/--input.

Optional Arguments:
  -p, --platforms PLATFORMS     The platforms from which to retrieve links
                                (facebook, instagram, or reddit). This value can
                                be comma-separated.
  --posts POSTS                 Path to a file containing the retrieved posts.
  --rate-limit RATE_LIMIT       Authorized number of hits by minutes. Defaults
                                to `6`. Can also be configured in a .minetrc
                                file as "crowdtangle.rate_limit" or read from
                                the MINET_CROWDTANGLE_RATE_LIMIT env variable.
  --sort-by {date,subscriber_count,total_interactions}
                                How to sort retrieved posts. Defaults to `date`.
  --start-date START_DATE       The earliest date at which a post could be
                                posted (UTC!). You can pass just a year or a
                                year-month for convenience. Defaults to `2010`.
  -t, --token TOKEN             CrowdTangle dashboard API token. Rcfile key:
                                crowdtangle.token. Can also be configured in a
                                .minetrc file as "crowdtangle.token" or read
                                from the MINET_CROWDTANGLE_TOKEN env variable.
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
                                the URLs you want to process. Will consider `-`
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Computing a summary of aggregated stats for urls contained in a CSV row:
    $ minet ct summary url urls.csv --token YOUR_TOKEN --start-date 2019-01-01 > summary.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet crowdtangle summary "value"

. Here is how to use a command with a CSV file:
    $ minet crowdtangle summary column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet crowdtangle summary column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet crowdtangle summary column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet crowdtangle summary "value1,value2" --explode ","
```

## Facebook

```
Usage: minet facebook [-h]
                      {comments,post-authors,post-stats,post,posts,url-likes}
                      ...

# Minet Facebook Command

Collect data from Facebook.

Optional Arguments:
  -h, --help                    show this help message and exit

Subcommands:
  {comments,post-authors,post-stats,post,posts,url-likes}
                                Subcommand to use.
```

<h3 id="facebook-comments">comments</h3>

```
Usage: minet facebook comments [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [--throttle THROTTLE] [-i INPUT]
                               [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                               [-o OUTPUT]
                               post_url_or_post_url_column

# Minet Facebook Comments Command

Scrape a Facebook post's comments.

This requires to be logged in to a Facebook account, so
by default this command will attempt to grab the relevant
authentication cookies from a local Firefox browser.

If you want to grab cookies from another browser or want
to directly pass the cookie as a string, check out the
-c/--cookie flag.

Positional Arguments:
  post_url_or_post_url_column   Single post url to process or name of the CSV
                                column containing post urls when using
                                -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "facebook.cookie" or read
                                from the MINET_FACEBOOK_COOKIE env variable.
  --throttle THROTTLE           Throttling time, in seconds, to wait between
                                each request. Defaults to `2.0`.
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
                                the post urls you want to process. Will consider
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Scraping a post's comments:
    $ minet fb comments https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

. Grabbing cookies from chrome:
    $ minet fb comments -c chrome https://www.facebook.com/groups/186982532676569/permalink/4096995827030341/ > comments.csv

. Scraping comments from multiple posts listed in a CSV file:
    $ minet fb comments post_url -i posts.csv > comments.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet facebook comments "value"

. Here is how to use a command with a CSV file:
    $ minet facebook comments column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet facebook comments column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet facebook comments column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet facebook comments "value1,value2" --explode ","
```

<h3 id="facebook-post">post</h3>

```
Usage: minet facebook post [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [--throttle THROTTLE] [-i INPUT] [--explode EXPLODE]
                           [-s SELECT] [--total TOTAL] [-o OUTPUT]
                           post_url_or_post_url_column

# Minet Facebook Post Command

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

Positional Arguments:
  post_url_or_post_url_column   Single post url to process or name of the CSV
                                column containing post urls when using
                                -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "facebook.cookie" or read
                                from the MINET_FACEBOOK_COOKIE env variable.
  --throttle THROTTLE           Throttling time, in seconds, to wait between
                                each request. Defaults to `2.0`.
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
                                the post urls you want to process. Will consider
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Scraping a post:
    $ minet fb post https://m.facebook.com/watch/?v=448540820705115 > post.csv

. Grabbing cookies from chrome:
    $ minet fb posts -c chrome https://m.facebook.com/watch/?v=448540820705115 > post.csv

. Scraping post from multiple urls listed in a CSV file:
    $ minet fb post url -i urls.csv > post.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet facebook post "value"

. Here is how to use a command with a CSV file:
    $ minet facebook post column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet facebook post column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet facebook post column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet facebook post "value1,value2" --explode ","
```

<h3 id="facebook-posts">posts</h3>

```
Usage: minet facebook posts [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [--throttle THROTTLE] [-i INPUT] [--explode EXPLODE]
                            [-s SELECT] [--total TOTAL] [-o OUTPUT]
                            group_url_or_group_url_column

# Minet Facebook Posts Command

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

Positional Arguments:
  group_url_or_group_url_column
                                Single group url to process or name of the CSV
                                column containing group urls when using
                                -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "facebook.cookie" or read
                                from the MINET_FACEBOOK_COOKIE env variable.
  --throttle THROTTLE           Throttling time, in seconds, to wait between
                                each request. Defaults to `2.0`.
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
                                the group urls you want to process. Will
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Scraping a group's posts:
    $ minet fb posts https://www.facebook.com/groups/444175323127747 > posts.csv

. Grabbing cookies from chrome:
    $ minet fb posts -c chrome https://www.facebook.com/groups/444175323127747 > posts.csv

. Scraping posts from multiple groups listed in a CSV file:
    $ minet fb posts group_url -i groups.csv > posts.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet facebook posts "value"

. Here is how to use a command with a CSV file:
    $ minet facebook posts column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet facebook posts column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet facebook posts column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet facebook posts "value1,value2" --explode ","
```

<h3 id="facebook-post-authors">post-authors</h3>

```
Usage: minet facebook post-authors [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                   [--refresh-per-second REFRESH_PER_SECOND]
                                   [--throttle THROTTLE] [-i INPUT]
                                   [--explode EXPLODE] [-s SELECT]
                                   [--total TOTAL] [-o OUTPUT]
                                   post_url_or_post_url_column

# Minet Facebook Post Authors Command

Retrieve the author of the given Facebook posts.

Note that it is only relevant for group posts since
only administrators can post something on pages.

Positional Arguments:
  post_url_or_post_url_column   Single post to process or name of the CSV column
                                containing posts when using -i/--input.

Optional Arguments:
  -c, --cookie COOKIE           Authenticated cookie to use or browser from
                                which to extract it (supports "firefox",
                                "chrome", "chromium", "opera" and "edge").
                                Defaults to `firefox`. Can also be configured in
                                a .minetrc file as "facebook.cookie" or read
                                from the MINET_FACEBOOK_COOKIE env variable.
  --throttle THROTTLE           Throttling time, in seconds, to wait between
                                each request. Defaults to `2.0`.
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching authors of a series of posts in a CSV file:
    $ minet fb post-authors post_url -i fb-posts.csv > authors.csv

how to use the command with a CSV file?

> A lot of minet commands, including this one, can both be
> given a single value to process or a bunch of them if
> given the column of a CSV file passed to -i/--input instead.

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet facebook post-authors "value"

. Here is how to use a command with a CSV file:
    $ minet facebook post-authors column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet facebook post-authors column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet facebook post-authors column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet facebook post-authors "value1,value2" --explode ","
```

<h3 id="facebook-url-likes">url-likes</h3>

```
Usage: minet facebook url-likes [-h] [--silent]
                                [--refresh-per-second REFRESH_PER_SECOND]
                                [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                [--total TOTAL] [-o OUTPUT]
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
    $ xsv search -s col . | minet facebook url-likes column_name -i -

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
```

<h3 id="google-sheets">sheets</h3>

```
Usage: minet google sheets [-h] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [-a AUTHUSER] [-c COOKIE] [-o OUTPUT]
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

<h3 id="hyphe-declare">declare</h3>

```
Usage: minet hyphe declare [-h] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [--password PASSWORD] [--total TOTAL] [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Declaring webentities from a Hyphe export:
    $ minet hyphe declare http://myhyphe.com/api/ target-corpus export.csv
```

<h3 id="hyphe-destroy">destroy</h3>

```
Usage: minet hyphe destroy [-h] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND]
                           [--password PASSWORD] [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Destroying a corpus:
    $ minet hyphe destroy http://myhyphe.com/api/ my-corpus
```

<h3 id="hyphe-dump">dump</h3>

```
Usage: minet hyphe dump [-h] [--silent]
                        [--refresh-per-second REFRESH_PER_SECOND]
                        [-O OUTPUT_DIR] [--body] [--statuses STATUSES]
                        [--page-count PAGE_COUNT] [--password PASSWORD]
                        [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Dumping a corpus into the ./corpus directory:
    $ minet hyphe dump http://myhyphe.com/api/ corpus-name -O corpus
```

<h3 id="hyphe-reset">reset</h3>

```
Usage: minet hyphe reset [-h] [--silent]
                         [--refresh-per-second REFRESH_PER_SECOND]
                         [--password PASSWORD] [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Resetting a corpus:
    $ minet hyphe reset http://myhyphe.com/api/ my-corpus
```

<h3 id="hyphe-tag">tag</h3>

```
Usage: minet hyphe tag [-h] [--silent] [--refresh-per-second REFRESH_PER_SECOND]
                       [--separator SEPARATOR] [--password PASSWORD]
                       [--total TOTAL] [-o OUTPUT]
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
                       {comments,hashtag,post-infos,user-followers,user-following,user-infos,user-posts}
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Subcommands:
  {comments,hashtag,post-infos,user-followers,user-following,user-infos,user-posts}
                                Subcommand to use.
```

<h3 id="insta-comments">comments</h3>

```
Usage: minet instagram comments [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                [--refresh-per-second REFRESH_PER_SECOND]
                                [-l LIMIT] [-i INPUT] [--explode EXPLODE]
                                [-s SELECT] [--total TOTAL] [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet instagram comments column_name -i -

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
                               [-l LIMIT] [-i INPUT] [--explode EXPLODE]
                               [-s SELECT] [--total TOTAL] [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet instagram hashtag column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram hashtag column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram hashtag "value1,value2" --explode ","
```

<h3 id="insta-post-infos">post-infos</h3>

```
Usage: minet instagram post-infos [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet instagram post-infos column_name -i -

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
                                      [-l LIMIT] [-i INPUT] [--explode EXPLODE]
                                      [-s SELECT] [--total TOTAL] [-o OUTPUT]
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

If a username is a number without '@' at the begining, it will be
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet instagram user-followers column_name -i -

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
                                      [-l LIMIT] [-i INPUT] [--explode EXPLODE]
                                      [-s SELECT] [--total TOTAL] [-o OUTPUT]
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

If a username is a number without '@' at the begining, it will be
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet instagram user-following column_name -i -

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
                                  [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                  [--total TOTAL] [-o OUTPUT]
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

If a username is a number without '@' at the begining, it will be
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet instagram user-infos column_name -i -

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
                                  [-l LIMIT] [-i INPUT] [--explode EXPLODE]
                                  [-s SELECT] [--total TOTAL] [-o OUTPUT]
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

If a username is a number without '@' at the begining, it will be
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet instagram user-posts column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet instagram user-posts column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet instagram user-posts "value1,value2" --explode ","
```

## Mediacloud

<h3 id="mc-medias">medias</h3>

```
Usage: minet mediacloud medias [-h] [-t TOKEN] [--rcfile RCFILE] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [--feeds FEEDS] [-i INPUT] [--explode EXPLODE]
                               [-s SELECT] [--total TOTAL] [-o OUTPUT]
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
    $ xsv search -s col . | minet mediacloud medias column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet mediacloud medias column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet mediacloud medias "value1,value2" --explode ","
```

<h3 id="mc-search">search</h3>

```
Usage: minet mediacloud search [-h] [-t TOKEN] [--rcfile RCFILE] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND]
                               [-c COLLECTIONS] [--filter-query FILTER_QUERY]
                               [-m MEDIAS] [--publish-day PUBLISH_DAY]
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
                                      [--media-id MEDIA_ID]
                                      [--from-media-id FROM_MEDIA_ID]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit
```

## Telegram

### channel-infos

```
Usage: minet telegram channel-infos [-h] [--throttle THROTTLE] [--silent]
                                    [--refresh-per-second REFRESH_PER_SECOND]
                                    [-i INPUT] [--explode EXPLODE] [-s SELECT]
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
    $ xsv search -s col . | minet telegram channel-infos column_name -i -

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
                                       [-i INPUT] [--explode EXPLODE]
                                       [-s SELECT] [--total TOTAL] [-o OUTPUT]
                                       channel_name_or_channel_name_column

# Minet Telegram Channel-Messages Command

Scrape Telegram channel messages.

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
    $ xsv search -s col . | minet telegram channel-messages column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet telegram channel-messages column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet telegram channel-messages "value1,value2" --explode ","
```

## Tiktok

```
Usage: minet tiktok [-h] {search-videos} ...

# Minet Tiktok Command

Gather data from Tiktok.

Optional Arguments:
  -h, --help       show this help message and exit

Subcommands:
  {search-videos}  Subcommand to use.
```

### search-videos

```
Usage: minet tiktok search-videos [-h] [-c COOKIE] [--rcfile RCFILE] [--silent]
                                  [--refresh-per-second REFRESH_PER_SECOND]
                                  [-l LIMIT] [-i INPUT] [--explode EXPLODE]
                                  [-s SELECT] [--total TOTAL] [-o OUTPUT]
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet tiktok search-videos column_name -i -

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
                               [--retweeted-id RETWEETED_ID] [--ids]
                               [--api-key API_KEY] [--rcfile RCFILE]
                               [--api-secret-key API_SECRET_KEY]
                               [--access-token ACCESS_TOKEN]
                               [--access-token-secret ACCESS_TOKEN_SECRET]
                               [-i INPUT] [--explode EXPLODE] [-s SELECT]
                               [--total TOTAL] [--resume] [-o OUTPUT]
                               tweet_url_or_id_or_tweet_url_or_id_column

# Minet Twitter Attrition Command

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
  --resume                      "Whether to resume from an aborted collection.
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
    $ xsv search -s col . | minet twitter attrition column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter attrition column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter attrition "value1,value2" --explode ","
```

### followers

```
Usage: minet twitter followers [-h] [--ids] [--silent]
                               [--refresh-per-second REFRESH_PER_SECOND] [--v2]
                               [--api-key API_KEY] [--rcfile RCFILE]
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
  --resume                      "Whether to resume from an aborted collection.
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
    $ xsv search -s col . | minet twitter followers column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter followers column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter followers "value1,value2" --explode ","
```

### friends

```
Usage: minet twitter friends [-h] [--ids] [--silent]
                             [--refresh-per-second REFRESH_PER_SECOND] [--v2]
                             [--api-key API_KEY] [--rcfile RCFILE]
                             [--api-secret-key API_SECRET_KEY]
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
  --resume                      "Whether to resume from an aborted collection.
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
    $ xsv search -s col . | minet twitter friends column_name -i -

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
    $ xsv search -s col . | minet twitter list-followers column_name -i -

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
    $ xsv search -s col . | minet twitter list-members column_name -i -

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
                                [--api-key API_KEY] [--rcfile RCFILE]
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
    $ xsv search -s col . | minet twitter retweeters column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter retweeters column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter retweeters "value1,value2" --explode ","
```

<h3 id="twitter-scrape">scrape</h3>

```
Usage: minet twitter scrape [-h] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [--include-refs] [-l LIMIT]
                            [--query-template QUERY_TEMPLATE] [-c COOKIE]
                            [--rcfile RCFILE] [--timezone TIMEZONE] [-i INPUT]
                            [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                            [-o OUTPUT]
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
    $ xsv search -s col . | minet twitter scrape column_name -i -

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
                                [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                [--total TOTAL] [-o OUTPUT]
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
    $ xsv search -s col . | minet twitter tweet-date column_name -i -

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
                                  [--until-id UNTIL_ID]
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
                                will be counted. The date should have the format
                                : "YYYY-MM-DDTHH:mm:ssZ" but incomplete dates
                                will be completed for you e.g. "2002-04".
  --since-id SINCE_ID           Will return tweets with ids that are greater
                                than the specified id. Takes precedence over
                                --start-time.
  --sort-order {recency,relevancy}
                                How to sort retrieved tweets. Defaults to
                                `recency`.
  --start-time START_TIME       The oldest UTC datetime from which the tweets
                                will be counted. The date should have the format
                                : "YYYY-MM-DDTHH:mm:ssZ" but incomplete dates
                                will be completed for you e.g. "2002-04".
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
    $ xsv search -s col . | minet twitter tweet-search column_name -i -

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
                                 [--since-id SINCE_ID] [--until-id UNTIL_ID]
                                 [--start-time START_TIME] [--end-time END_TIME]
                                 [--academic] [--api-key API_KEY]
                                 [--rcfile RCFILE]
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
                                will be counted. The date should have the format
                                : "YYYY-MM-DDTHH:mm:ssZ" but incomplete dates
                                will be completed for you e.g. "2002-04".
  --granularity {day,hour,minute}
                                Granularity used to group the data by. Defaults
                                to `day`.
  --since-id SINCE_ID           Will return tweets with ids that are greater
                                than the specified id. Takes precedence over
                                --start-time.
  --start-time START_TIME       The oldest UTC datetime from which the tweets
                                will be counted. The date should have the format
                                : "YYYY-MM-DDTHH:mm:ssZ" but incomplete dates
                                will be completed for you e.g. "2002-04".
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
    $ xsv search -s col . | minet twitter tweet-count column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter tweet-count column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter tweet-count "value1,value2" --explode ","
```

### tweets

```
Usage: minet twitter tweets [-h] [--v2] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [--timezone TIMEZONE] [--api-key API_KEY]
                            [--rcfile RCFILE] [--api-secret-key API_SECRET_KEY]
                            [--access-token ACCESS_TOKEN]
                            [--access-token-secret ACCESS_TOKEN_SECRET]
                            [-i INPUT] [--explode EXPLODE] [-s SELECT]
                            [--total TOTAL] [--resume] [-o OUTPUT]
                            tweet_id_or_tweet_id_column

# Minet Twitter Tweets Command

Collecting tweet metadata from the given tweet ids, using the API.

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
                                the tweet ids you want to process. Will consider
                                `-` as stdin.
  -o, --output OUTPUT           Path to the output file. Will consider `-` as
                                stdout. If not given, results will also be
                                printed to stdout.
  --resume                      "Whether to resume from an aborted collection.
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
    $ xsv search -s col . | minet twitter tweets column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet twitter tweets column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet twitter tweets "value1,value2" --explode ","
```

### users

```
Usage: minet twitter users [-h] [--ids] [--silent]
                           [--refresh-per-second REFRESH_PER_SECOND] [--v2]
                           [--timezone TIMEZONE] [--api-key API_KEY]
                           [--rcfile RCFILE] [--api-secret-key API_SECRET_KEY]
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
  --resume                      "Whether to resume from an aborted collection.
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
    $ xsv search -s col . | minet twitter users column_name -i -

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
                                 [--api-key API_KEY] [--rcfile RCFILE]
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
    $ xsv search -s col . | minet twitter user-search column_name -i -

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
                                 [--min-date MIN_DATE] [--exclude-retweets]
                                 [--v2] [--timezone TIMEZONE]
                                 [--api-key API_KEY] [--rcfile RCFILE]
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
    $ xsv search -s col . | minet twitter user-tweets column_name -i -

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
                                 --end-date END_DATE [--agent AGENT]
                                 [--access ACCESS] [-t THREADS]
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
  --resume                      "Whether to resume from an aborted collection.
                                Need -o to be set. Will only work with --sum.
  --refresh-per-second REFRESH_PER_SECOND
                                Number of times to refresh the progress bar per
                                second. Can be a float e.g. `0.5` meaning once
                                every two seconds. Use this to limit CPU usage
                                when launching multiple commands at once.
                                Defaults to `10`.
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
    $ xsv search -s col . | minet wikipedia pageviews column_name -i -

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
                              [-i INPUT] [--explode EXPLODE] [-s SELECT]
                              [--total TOTAL] [-o OUTPUT]
                              video_or_video_column

# Youtube captions

Retrieve captions for the given YouTube videos.

Positional Arguments:
  video_or_video_column         Single video url or id to process or name of the
                                CSV column containing video urls or ids when
                                using -i/--input.

Optional Arguments:
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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

Examples:

. Fetching captions for a list of videos:
    $ minet yt captions video_id videos.csv > captions.csv

. Fetching French captions with a fallback to English:
    $ minet yt captions video_id videos.csv --lang fr,en > captions.csv

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
    $ xsv search -s col . | minet youtube captions column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube captions column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube captions "value1,value2" --explode ","
```

### channel-videos

```
Usage: minet youtube channel-videos [-h] [-k KEY] [--rcfile RCFILE] [--silent]
                                    [--refresh-per-second REFRESH_PER_SECOND]
                                    [-i INPUT] [--explode EXPLODE] [-s SELECT]
                                    [--total TOTAL] [-o OUTPUT]
                                    channel_or_channel_column

# Youtube channel videos

Retrieve metadata about all Youtube videos from one or many channel(s) using the API.

Under the hood, this command extract the channel id from the given url or scrape the
website to find it if necessary. Then the command uses the API to retrieve
information about videos stored in the main playlist of the channel
supposed to contain all the channel's videos.

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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

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

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet youtube channel-videos "value"

. Here is how to use a command with a CSV file:
    $ minet youtube channel-videos column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet youtube channel-videos column_name -i -

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
                              [-i INPUT] [--explode EXPLODE] [-s SELECT]
                              [--total TOTAL] [-o OUTPUT]
                              channel_or_channel_column

# Youtube Channels Command

Retrieve metadata about Youtube channel from one or many name(s) using the API.

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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

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

> Note that when given a CSV file as input, minet will
> concatenate the input file columns with the ones added
> by the command. You can always restrict the input file
> columns to keep by using the -s/--select flag.

. Here is how to use a command with a single value:
    $ minet youtube channels "value"

. Here is how to use a command with a CSV file:
    $ minet youtube channels column_name -i file.csv

. Here is how to read CSV file from stdin using `-`:
    $ xsv search -s col . | minet youtube channels column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube channels column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube channels "value1,value2" --explode ","
```

<h3 id="youtube-comments">comments</h3>

```
Usage: minet youtube comments [-h] [-k KEY] [--rcfile RCFILE] [--silent]
                              [--refresh-per-second REFRESH_PER_SECOND]
                              [-i INPUT] [--explode EXPLODE] [-s SELECT]
                              [--total TOTAL] [-o OUTPUT]
                              video_or_video_column

# Youtube comments

Retrieve metadata about Youtube comments using the API.

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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet youtube comments column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube comments column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube comments "value1,value2" --explode ","
```

<h3 id="youtube-search">search</h3>

```
Usage: minet youtube search [-h] [-l LIMIT] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND]
                            [--order {date,rating,relevance,title,videoCount,viewCount}]
                            [-k KEY] [--rcfile RCFILE] [-i INPUT]
                            [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                            [-o OUTPUT]
                            query_or_query_column

# Youtube search

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
  --silent                      Whether to suppress all the log and progress
                                bars. Can be useful when piping.
  -h, --help                    show this help message and exit

example:

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
    $ xsv search -s col . | minet youtube search column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube search column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube search "value1,value2" --explode ","
```

### videos

```
Usage: minet youtube videos [-h] [-k KEY] [--rcfile RCFILE] [--silent]
                            [--refresh-per-second REFRESH_PER_SECOND] [-i INPUT]
                            [--explode EXPLODE] [-s SELECT] [--total TOTAL]
                            [-o OUTPUT]
                            video_or_video_column

# Youtube videos

Retrieve metadata about Youtube videos using the API.

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
    $ xsv search -s col . | minet youtube videos column_name -i -

. Here is how to indicate that the CSV column may contain multiple
  values separated by a special character:
    $ minet youtube videos column_name -i file.csv --explode "|"

. This also works with single values:
    $ minet youtube videos "value1,value2" --explode ","
```

